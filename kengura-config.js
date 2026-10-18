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
  url: "https://fmgajzmlmmqlxghdluix.supabase.co",
  anonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtZ2Fqem1sbW1xbHhnaGRsdWl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTIzMTcwMDksImV4cCI6MjEwNzg5MzAwOX0.cczf3Bi54KEPvbLZVWIwxAd2IrIp-WYI4SPIZ0DW8fs"
};
