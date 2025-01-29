## Developing

# make sure you have deno installed - https://deno.land/

1. Install required dependencies
   `deno install`
2. Run the server

```bash
deno run dev
```

## Building

To create a production version of your app:

```bash
deno run build
```

You can preview the production build with `deno run preview`.

## Deployment to Render.com

1. Fork or push this repository to your Git provider (GitHub, GitLab, etc.)
2. Create a new Web Service on Render.com
3. Connect your repository
4. Configure the following settings:
   - Build Command: `deno run build`
   - Start Command: `node build/index.js`
5. Add the following environment variables in Render.com dashboard:
   - `NODE_ENV`: production
   - `PUBLIC_API_URL`: Your API endpoint URL

The application will be automatically deployed when you push changes to your repository.
