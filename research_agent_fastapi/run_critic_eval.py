import asyncio
import datetime
import uuid
from .critic_eval import critic_eval_set
from .nodes import critic_node
from .state import ResearchState
from langsmith import Client


async def run_critic_eval():
    client = Client()
    results = []

    for case in critic_eval_set:
        test_state: ResearchState = {
            "messages": [],
            "topic": "test topic",
            "findings": case["findings"],
            "draft": case["draft"],
            "feedback": "",
            "verdict": "",
            "revision_count": 0
        }

        run_id = uuid.uuid4()
        start_time = datetime.datetime.now(datetime.timezone.utc)
        output = await critic_node(test_state)
        end_time = datetime.datetime.now(datetime.timezone.utc)
        actual_verdict = output["verdict"]
        passed = actual_verdict == case["expected_verdict"]

        results.append({
            "name": case["name"],
            "expected": case["expected_verdict"],
            "actual": actual_verdict,
            "passed": passed,
            "feedback": output["feedback"]
        })
        client.create_run(
            id=run_id,
            name=f"critic-eval-{case['name']}",
            run_type="chain",
            start_time=start_time,
            inputs={
                "findings": case["findings"],
                "draft": case["draft"]
            },
            output={
                "verdict": actual_verdict,
                "expected": case["expected_verdict"],
                "passed": passed
            },
            tags=["critic-eval"]
        )

        client.update_run(
            run_id=run_id,
            end_time=end_time,
            outputs={
                "verdict": actual_verdict,
                "passed": passed
            }
        )

    print("=" * 70)
    print("CRITIC EVALUATION REPORT")
    print("=" * 70)

    hits = 0
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        if r["passed"]:
            hits += 1
        print(f"\n[{status}] {r['name']}")
        print(f"  Expected: {r['expected']} | Actual: {r['actual']}")
        if not r["passed"]:
            print(f"  Critic said: {r['feedback']}")

    print("\n" + "=" * 70)
    print(f"Accuracy: {hits}/{len(critic_eval_set)} ({hits/len(critic_eval_set):.0%})")
    print("=" * 70)

    return results


if __name__ == "__main__":
    asyncio.run(run_critic_eval())