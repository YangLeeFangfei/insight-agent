class OpenAICompatibleLLMClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        sdk_client=None,
    ) -> None:
        if sdk_client is None:
            from openai import OpenAI

            sdk_client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )

        self.model = model
        self.sdk_client = sdk_client

    def complete(self, prompt: str) -> str:
        response = self.sdk_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content or ""
