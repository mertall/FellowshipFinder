const API_BASE_URL = "http://localhost:8000";

/**
 * Generalized function to make API requests.
 */
async function fetchAPI(endpoint, method = "GET", body = null) {
    try {
        const options = {
            method,
            headers: { "Content-Type": "application/json" },
        };

        if (body) options.body = JSON.stringify(body);

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("API Request Failed:", error);
        return { error: "Something went wrong. Please try again." };
    }
}

/**
 * Search for fellowships based on university and field of study.
 */
export async function searchFellowships(university, fieldOfStudy) {
    return fetchAPI("/search", "POST", { university, field_of_study: fieldOfStudy });
}

/**
 * Fetch the list of universities and their fellowship resource links.
 */
export async function fetchUniversities() {
    return fetchAPI("/universities");
}
