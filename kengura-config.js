/* Parent accounts (optional). Empty values = no accounts: progress stays
   in this browser only, exactly as before.

   To switch accounts on (one-time, about 10 minutes):
   1. Create a free project at https://supabase.com (Region: EU, e.g. Frankfurt).
   2. Project → SQL Editor → paste cloud-setup.sql → Run.
   3. Authentication → URL Configuration → Site URL = the address of this app
      (e.g. https://<your-site>.netlify.app/); add the same under Redirect URLs.
   4. Project Settings → API → copy "Project URL" and the "anon public" key
      into the two fields below, commit and deploy.
   The anon key is meant to be public: what each parent can read or change
   is enforced in the database (row level security in cloud-setup.sql). */
window.KENGURA_CLOUD = {
  url: "",
  anonKey: ""
};
