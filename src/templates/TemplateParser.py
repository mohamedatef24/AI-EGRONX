class TemplateParser:

    def __init__(self):
        # Default English RAG templates
        self.templates = {
            "rag": {
                "system_prompt": (
                    "You are a helpful assistant that answers strictly based on the provided documents. "
                    "If the answer cannot be found, say you don't know."
                ),
                "document_prompt": "Document {{doc_num}}:\n{{chunk_text}}",
                "footer_prompt": (
                    "Using the documents above, answer the user's question concisely and accurately."
                ),
            }
        }

    def get(self, section: str, key: str, variables: dict = None):
        template = self.templates.get(section, {}).get(key, "")
        if not variables:
            return template
        # Minimal templating using double braces {{var}}
        result = template
        for k, v in variables.items():
            result = result.replace(f"{{{{{k}}}}}", str(v))
        return result


