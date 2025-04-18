# Deploying to Streamlit Cloud

This guide provides step-by-step instructions for deploying the Book Summarizer application to Streamlit Cloud.

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A [Streamlit Cloud](https://streamlit.io/cloud) account (can use your GitHub account to sign up)
4. [OpenAI API key](https://platform.openai.com/account/api-keys)
5. [Miro Access Token](https://miro.com/app/settings/user-profile/apps) (optional, for mind map functionality)

## Deployment Files (Already Set Up)

The following files are already configured for deployment:

- `requirements.txt` - Lists all Python dependencies
- `runtime.txt` - Specifies Python 3.9 for compatibility
- `Procfile` - Defines the command to run the Streamlit app
- `.streamlit/config.toml` - Configures Streamlit settings

## Deployment Steps

1. **Push your code to GitHub**
   ```
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push
   ```

2. **Log in to Streamlit Cloud**
   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account

3. **Deploy a new app**
   - Click "New app"
   - Select your GitHub repository
   - Set the main file path to `app/app.py`
   - Click "Deploy"

4. **Set up Secrets**
   In the Streamlit Cloud dashboard:
   - Go to your app settings
   - Under "Secrets", add the following in TOML format:
     ```toml
     [api_keys]
     openai = "your-openai-api-key"
     miro = "your-miro-access-token"
     ```

5. **Advanced Settings (Optional)**
   - Set a custom subdomain if desired
   - Configure resource limits (if you have a paid account)

## Troubleshooting

- **Package Installation Issues**: Check that all required packages are listed in `requirements.txt` with correct versions.
- **Python Version Problems**: Ensure `runtime.txt` specifies a supported Python version (3.9 is recommended for this app).
- **API Key Issues**: Verify that your secrets are correctly formatted in TOML syntax.
- **Miro Integration Errors**: Ensure your Miro token has the correct permissions (boards:read, boards:write, boards:create).

## Local Testing Before Deployment

Run locally to verify everything works:

```bash
streamlit run app/app.py
```

## Updating Your Deployed App

Any changes pushed to the main branch of your GitHub repository will automatically trigger a redeployment on Streamlit Cloud. 