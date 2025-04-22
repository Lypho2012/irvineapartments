import './App.css';
import React, { useEffect, useState } from 'react';

import axios from "axios";

function App() {
  const [prevEmailDate,setPrevEmailDate] = useState(null)
  useEffect(() => {
    const checkTime = () => {
      const now = new Date();
      const currentHour = now.getHours();
      const currentMinute = now.getMinutes();
      console.log(currentHour,currentMinute)
      if (currentHour >= 9 && (!prevEmailDate || prevEmailDate.getDate() != now.getDate() && prevEmailDate.getMonth() != now.getMonth() && prevEmailDate.getFullYear() != now.getFullYear())) {
        console.log("Getting today's report...");
        axios.post('http://localhost:8000/get-today-report');
        setPrevEmailDate(now);
      }
    }
    const intervalId = setInterval(checkTime, 6000);
    return () => clearInterval(intervalId);
  })
  return (
    <div>

    </div>
  );
}

export default App;
