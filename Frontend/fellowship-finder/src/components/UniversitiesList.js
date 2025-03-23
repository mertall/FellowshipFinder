import React, { useEffect, useState } from "react";
import { fetchUniversities } from "../api/api";

const UniversitiesList = () => {
  const [universities, setUniversities] = useState([]);

  useEffect(() => {
    const loadUniversities = async () => {
      const data = await fetchUniversities();
      if (data.universities) setUniversities(data.universities);
    };
    loadUniversities();
  }, []);

  return (
    <div className="bg-gray-900 p-6 rounded-lg shadow-lg text-center mt-6">
      <h2 className="text-2xl font-bold mb-4">Supported Universities</h2>
      <ul className="space-y-2">
        {universities.map((uni, index) => (
          <li key={index}>
            <a
              href={uni.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:underline"
            >
              {uni.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UniversitiesList;
