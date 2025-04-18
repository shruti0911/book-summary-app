# Book Summarizer

A Streamlit application that summarizes non-fiction books and creates mind maps in Miro.

## Features

- Upload PDF files of non-fiction books
- Generate detailed summaries using OpenAI
- Create visual mind maps in Miro
- Option to download summaries as text files

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run app/app.py`

## Deployment to Streamlit Cloud

This application is configured for easy deployment to Streamlit Cloud:

1. Make sure your GitHub repository includes:
   - `requirements.txt` (in the root directory)
   - `runtime.txt` (specifies Python 3.9)
   - `Procfile` (contains `web: streamlit run app/app.py`)

2. Connect your GitHub repository to Streamlit Cloud
3. Set the required secrets in the Streamlit Cloud dashboard:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `MIRO_ACCESS_TOKEN` - Your Miro access token (if using Miro integration)

## Environment Variables

Create a `.streamlit/secrets.toml` file locally with the following structure:

```toml
[api_keys]
openai = "your-openai-api-key"
miro = "your-miro-access-token"
```

## License

MIT 