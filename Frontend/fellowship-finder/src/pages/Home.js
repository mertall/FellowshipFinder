import React, { useState } from "react";
import { searchFellowships } from "../api/api";
import FellowshipTable from "../components/FellowshipTable";
import UniversitiesList from "../components/UniversitiesList";

const Home = () => {
  const [university, setUniversity] = useState("Unviersity of Chicago");
  const [fieldOfStudy, setFieldOfStudy] = useState("");
  const [fellowships, setFellowships] = useState([]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const response = await searchFellowships(university, fieldOfStudy);
    setFellowships(response.fellowships);
  };

  return (
    <div className="w-full max-w-2xl bg-gray-900 p-8 rounded-lg shadow-lg text-center">
      <h1 className="text-4xl font-bold mb-6">Fellowship Finder</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          value={university}
          onChange={(e) => setUniversity(e.target.value)}
          placeholder="Enter University"
          className="w-full p-3 bg-gray-800 border border-gray-600 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="text"
          value={fieldOfStudy}
          onChange={(e) => setFieldOfStudy(e.target.value)}
          placeholder="Enter Field of Study"
          className="w-full p-3 bg-gray-800 border border-gray-600 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="w-full p-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded transition duration-200"
        >
          Search
        </button>
      </form>

      {fellowships.length > 0 && (
        <div className="mt-6">
          <FellowshipTable fellowships={fellowships} />
        </div>
      )}

      {/* Add the Universities List Below */}
      <UniversitiesList />
    </div>
  );
};

export default Home;
