import React from "react";

const FellowshipTable = ({ fellowships }) => {
  return (
    <table className="border-collapse w-full border border-gray-300">
      <thead>
        <tr className="bg-gray-200">
          <th className="border border-gray-300 px-4 py-2">Name</th>
          <th className="border border-gray-300 px-4 py-2">Description</th>
          <th className="border border-gray-300 px-4 py-2">Link</th>
        </tr>
      </thead>
      <tbody>
        {fellowships.map((fellowship, index) => (
          <tr key={index} className="hover:bg-gray-100">
            <td className="border border-gray-300 px-4 py-2">{fellowship.name}</td>
            <td className="border border-gray-300 px-4 py-2">{fellowship.description}</td>
            <td className="border border-gray-300 px-4 py-2">
              <a href={fellowship.link} target="_blank" rel="noopener noreferrer" className="text-blue-500">View</a>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default FellowshipTable;
