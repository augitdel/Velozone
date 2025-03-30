import React, { useState, useEffect } from "react";
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://strada.sportsdatascience.be:8090';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzQwOTU2NDAwLAogICJleHAiOiAxODk4NzIyODAwCn0.jmTPjhaI3K_rugPcAe4PrHOWQqytNzNRwxpirHQZ4bA';
const ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYTlkMzY4NC1kYjkxLTRmYTEtYWY5Ni02OTExZTE1NjBjMDEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoyMDU2NjI5MDM2LCJpYXQiOjE3NDEyNjkwMzYsImVtYWlsIjoiZXhjZWxsZW50aWVAdWdlbnQuYmUiLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl0sInVzZXJyb2xlIjpbImxhcHJlYWRlciJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3NDEyNjkwMzZ9XSwic2Vzc2lvbl9pZCI6ImVkYTkwNGMyLTllYjUtNDM0YS04ZGZlLWQxMjkyMDA3Y2FmMiIsImlzX2Fub255bW91cyI6ZmFsc2V9.gqakyr5TWpknfPJ1fG107B3qm0hIGFg47kwvj3EjcoI';
const REFRESH_TOKEN = '0iw1_TL1yWfwZvY_iDs9Sw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const LiveSupabase = () => {
  const [lapTimes, setLapTimes] = useState([]);
  const [currentTime, setCurrentTime] = useState("");
  const [tags, setTags] = useState({});

  // Update the current time every 500ms
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const formattedTime = now.toLocaleTimeString("en-GB", { hour12: false });
      setCurrentTime(formattedTime);
    }, 500);

    return () => clearInterval(interval);
  }, []);

  // Set session and fetch data
  useEffect(() => {
    const setSupabaseSession = async () => {
      // Check if there's an active session
      supabase.auth.setSession(ACCESS_TOKEN, REFRESH_TOKEN);
      const session = supabase.auth.getSession(ACCESS_TOKEN, REFRESH_TOKEN);
      console.log('Current session:', session);

      if (!session) {
        // Set session with the provided tokens if no active session
        console.log('Setting new session...');
        const { error } = await supabase.auth.setSession(ACCESS_TOKEN, REFRESH_TOKEN);
        if (error) {
          console.error('Error setting session:', error.message);
        } else {
          console.log('Session set successfully');
        }
      }

      // Fetch lap times from the database
      const fetchLapTimes = async () => {
        const { data, error } = await supabase.from('laptimes').select('*');
        if (error) {
          console.error('Error fetching lap times:', error.message);
        } else {
          setLapTimes(data);
        }
      };

      // Fetch tags (if needed)
      const fetchTags = async () => {
        const { data, error } = await supabase.from('tags').select('*');
        if (error) {
          console.error('Error fetching tags:', error.message);
        } else {
          const tagsObject = data.reduce((acc, tag) => {
            acc[tag.id] = tag;
            return acc;
          }, {});
          setTags(tagsObject);
        }
      };

      fetchLapTimes();
      fetchTags();
    };

    setSupabaseSession();
  }, []);

  return (
    <div>
      <h1>Lap Times</h1>
      <ul>
        {lapTimes.map((record) => (
          <li key={record.id}>{record.lapTime}</li>
        ))}
      </ul>
      <h2>Current Time: {currentTime}</h2>
    </div>
  );
};

export default LiveSupabase;

