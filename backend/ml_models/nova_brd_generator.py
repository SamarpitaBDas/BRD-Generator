"""
nova_brd_generator.py
~~~~~~~~~~~~~~~~~~~~~
Amazon Nova 2 Lite BRD generator via Amazon Bedrock Runtime.

Architecture:
    Frontend (form input)
        → POST /api/generate-brd/
        → NovaBRDGenerator.generate()
        → Amazon Bedrock Runtime (us-east-1)
        → global.amazon.nova-2-lite-v1:0
        → Structured BRD text returned to frontend

AWS credentials are resolved automatically in this order (standard boto3 chain):
    1. Environment variables  AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN
    2. ~/.aws/credentials  (aws configure)
    3. IAM instance / task role (EC2, ECS, Lambda)

Set AWS_DEFAULT_REGION=us-east-1 or pass region= to NovaBRDGenerator().
"""

import json
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

MODEL_ID = "global.amazon.nova-2-lite-v1:0"
DEFAULT_REGION = "us-east-1"


def build_brd_prompt(
    product_name: str,
    problem_statement: str,
    target_users: str,
    key_features: str,
) -> str:
    """
    Build the structured prompt sent to Nova 2 Lite.

    Example output (truncated):
        You are a senior business analyst ...
        Product Name: SmartInventory
        ...
        Generate a complete BRD with the following sections: ...
    """
    return f"""You are a senior business analyst. Your task is to generate a professional, \
structured Business Requirements Document (BRD) based on the inputs provided.

---
Product Name: {product_name}
Problem Statement: {problem_statement}
Target Users: {target_users}
Key Features: {key_features}
---

Generate a complete BRD with EXACTLY the following sections in order. \
Use the section headings exactly as written. Be specific, professional, and concise.

1. Introduction
   - Purpose of the document
   - Background and context
   - Document scope

2. Scope
   - In-scope features and capabilities
   - Out-of-scope items
   - Assumptions

3. Stakeholders
   - List each stakeholder group with their role and interest in the project

4. Functional Requirements
   - Numbered list of specific functional requirements (FR-001, FR-002, ...)
   - Each requirement should be clear and testable

5. Non-Functional Requirements
   - Performance, security, scalability, reliability, usability requirements
   - Numbered NFR-001, NFR-002, ...

6. Success Metrics
   - Measurable KPIs to determine project success
   - Acceptance criteria

Output only the BRD content. Do not add any preamble or closing remarks outside the document.
"""


class NovaBRDGenerator:
    """
    Calls Amazon Nova 2 Lite via Bedrock Runtime to generate a BRD.

    Usage:
        generator = NovaBRDGenerator()
        brd_text = generator.generate(
            product_name="SmartInventory",
            problem_statement="Warehouses lack real-time stock visibility.",
            target_users="Warehouse managers and operations staff",
            key_features="Real-time tracking, alerts, reporting dashboard",
        )
    """

    def __init__(self, region: str = DEFAULT_REGION):
        self.region = region
        self._client = None  # lazy-initialised

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
            )
        return self._client

    def _build_request_body(self, prompt: str) -> dict:
        """
        Construct the Bedrock converse-style request body for Nova 2 Lite.

        Nova models use the Messages API format:
        {
            "messages": [{"role": "user", "content": [{"text": "..."}]}],
            "inferenceConfig": {"maxTokens": 4096, "temperature": 0.3}
        }
        """
        return {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            "inferenceConfig": {
                "maxTokens": 4096,
                "temperature": 0.3,   # lower = more deterministic / professional tone
                "topP": 0.9,
            },
        }

    def generate(
        self,
        product_name: str,
        problem_statement: str,
        target_users: str,
        key_features: str,
    ) -> str:
        """
        Generate a structured BRD and return it as plain text.

        Raises:
            RuntimeError – on Bedrock API errors or missing credentials.
        """
        prompt = build_brd_prompt(
            product_name=product_name,
            problem_statement=problem_statement,
            target_users=target_users,
            key_features=key_features,
        )

        request_body = self._build_request_body(prompt)

        logger.info("Invoking Nova 2 Lite for product: %s", product_name)

        try:
            response = self.client.invoke_model(
                modelId=MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body),
            )
        except NoCredentialsError as exc:
            logger.error("AWS credentials not found: %s", exc)
            raise RuntimeError(
                "AWS credentials not configured. "
                "Set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY or run 'aws configure'."
            ) from exc
        except ClientError as exc:
            error_code = exc.response["Error"]["Code"]
            logger.error("Bedrock ClientError [%s]: %s", error_code, exc)
            raise RuntimeError(f"Bedrock API error ({error_code}): {exc}") from exc

        raw = json.loads(response["body"].read())

        # Nova 2 Lite response shape:
        # { "output": { "message": { "content": [{"text": "..."}] } } }
        try:
            brd_text = raw["output"]["message"]["content"][0]["text"]
        except (KeyError, IndexError) as exc:
            logger.error("Unexpected Bedrock response shape: %s", raw)
            raise RuntimeError("Unexpected response format from Nova 2 Lite.") from exc

        logger.info("BRD generated successfully (%d chars)", len(brd_text))
        return brd_text.strip()
