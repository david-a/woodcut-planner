import type { Settings, WoodPiece, CalculationResult } from "../types/wood";

const API_BASE_URL = "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

interface CalculateRequest {
  settings: Settings;
  pieces: WoodPiece[];
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = "An error occurred";
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // Use default error message if JSON parsing fails
    }
    throw new ApiError(response.status, errorMessage);
  }
  return response.json();
}

export async function calculateCuts(
  request: CalculateRequest
): Promise<CalculationResult> {
  console.log("Making API request to:", `${API_BASE_URL}/calculate`);
  console.log("Request payload:", request);

  const response = await fetch(`${API_BASE_URL}/calculate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  console.log("Response status:", response.status);
  const result = await handleResponse<CalculationResult>(response);
  console.log("Response data:", result);
  return result;
}

// Health check endpoint to verify API connectivity
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
