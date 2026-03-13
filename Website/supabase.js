// ============================================================
// FLOWDESK — SUPABASE CONFIG
// Replace these two values with your project's URL and anon key
// Found at: supabase.com → your project → Settings → API
// ============================================================

const SUPABASE_URL = 'https://teovjlyddhbiauadojsa.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlb3ZqbHlkZGhiaWF1YWRvanNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMzNzE3MDYsImV4cCI6MjA4ODk0NzcwNn0.aAyj5pJIBkBVjgxxJwpiOFej-qZ3d_2taVwB_HAfik8';

const { createClient } = supabase;
const sb = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
