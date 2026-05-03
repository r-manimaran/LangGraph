
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Runtime

import sys
import time

#------------
# CONFIG
#------------

AGENT_NAME = "langgraph_claude_getting_started"
ENTRYPOINT = "langgraph_bedrock.py"
REQUIREMENTS = "requirements.txt"
TIMEOUT_SECONDS = 900 # 15 mins max time to wait

# -----------------
# Session / Region
# -----------------

boto_session = Session()

region = boto_session.region_name or "us-east-1"

print(f"[Info] Using region: {region}")

# --------------
# Init Runtime
# --------------
agentcore_runtime = Runtime()

# --------------
# Configure AGENT
# --------------
try:
    print("[Info] Configuring AgentCore runtime")

    response = agentcore_runtime.configure(
        entrypoint=ENTRYPOINT,
        auto_create_ecr=True,
        auto_create_execution_role=True,
        requirements_file=REQUIREMENTS,
        region=region,
        agent_name=AGENT_NAME
    )
    
    print("[Success] Agent configured successfully")
    print(f"Response: {response}")
except Exception as e:
    print(f"[Error] Failed to configure agent: {str(e)}")
    sys.exit(1)

# ---------------
# Launch Agent
# ---------------

try:
    print("[Info] Launching agent")

    launch_result = agentcore_runtime.launch()
    
    print("[Success] Agent launched successfully")
    print(f"Launch Result: {launch_result}")
except Exception as e:
    print(f"[Error] Failed to launch agent: {str(e)}")
    sys.exit(1)

# --------------------------
# Wait for Agent to be ready
# --------------------------

print(f"[Info] ⏰Waiting for agent to be ready (timeout: {TIMEOUT_SECONDS} seconds)")
start_time = time.time()
end_status = ["READY","CREATE_FAILED","DELETE_FAILED","UPDATE_FAILED"]

while True:
    try:
        status_response = agentcore_runtime.status()
        endpoint = status_response.endpoint
        status = endpoint.status if hasattr(endpoint, 'status') else endpoint["status"]
        
        print(f"[Info] Current agent status: {status}")

        if status in end_status:
            break
        
        if time.time() - start_time > TIMEOUT_SECONDS:
            print("[Error] ❌ Timeout waiting for agent to be ready")
            sys.exit(1)

    except Exception as e:
        print(f"[Error] ❌ Failed to check agent status: {str(e)}")
        sys.exit(1)


# -----------------
# Print Final Status
# ------------------

if status == "READY":
    print("[Success] ✅ Agent is ready to use")
    try:
        endpoint = status_response.endpoint
        print("\n 🎯Endpoint Details")
        print(endpoint)
    except Exception as e:
        pass
else:
    print(f"\n [Error] ❌ Agent deployment failed with status:{status}")
    sys.exit(1)