const API_BASE_URL = "http://127.0.0.1:8000";


export async function generateSRS(prompt: string) {
    const response = await fetch(`${API_BASE_URL}/api/srs/generate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            prompt: prompt,
        }),
    });

    if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
            `SRS generation failed: ${response.status} ${errorText}`
        );
    }

    return await response.json();
}