import boto3
import json
import time


# ================
# INIT
# ================
agent_arn = "arn:aws:bedrock-agentcore:us-east-1:395109667422:runtime/langgraph_claude_getting_started-eT9HMDBC6H"
agentcore_client = boto3.client(
    "bedrock-agentcore",
    region_name="us-east-1"
)
# "prompt":"What is 20+20?"
payload = {
    "prompt":"What is weather in Chennai?"
}

# -----------------
# INVOKE AGENT
# -----------------
try:
    boto3_response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        qualifier="DEFAULT",
        payload=json.dumps(payload)
    )
    runtime_session_id = boto3_response.get("runtimeSessionId")
    print(f"[INFO] Runtime Session ID:{runtime_session_id}")

    content_type = boto3_response.get("contentType","")

    # ------------------
    # STREAMING RESPONSE
    # ------------------

    if "event-stream" in content_type or "text/event-stream" in content_type:
        print("\n=== STREAMING RESPONSE ===")
        
        content = []
        stream = boto3_response.get("response")

        for event in stream:
            try:
                if "chunk" in event:
                    data = event["chunk"]["bytes"].decode("utf-8")
                    print(data, end="")
                    content.append(data)

            except Exception as e:
                print(f"\n[STREAM ERROR] {e}")

        final_output = "".join(content)

    # ------------------------
    # NON-STREAMING RESPONSE
    # ------------------------
    else:
        response_body =boto3_response.get("response")

        # response is usually StreamingBody
        raw = response_body.read().decode("utf-8")

        final_output = json.loads(raw)

        print("\n ----- OUTPUT -----")
        print(final_output)

except Exception as e:
    print(f"Error invoking agent: {e}")
    runtime_session_id = None

# ---------------------------
# STOP SESSION (SAFE CLEANUP)
# ---------------------------

try:
    if runtime_session_id:
        agentcore_client.stop_runtime_session(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=runtime_session_id,
            qualifier="DEFAULT"
        )
        print(f"\n ✅ Session '{runtime_session_id}' stopped successfully.")
    else:
        print(f"\n ⚠️ No session ID to stop")

except Exception as e:
        print(f"[Error] ❌ Failed to stop session: {e}")
