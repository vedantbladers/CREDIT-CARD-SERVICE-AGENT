const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8080';

export async function getTestToken() {
  const res = await fetch(`${GATEWAY_URL}/api/token/test`);
  if (!res.ok) {
    throw new Error(`Failed to fetch test token: HTTP ${res.status}`);
  }
  return res.json();
}

export async function sendChatMessage(message, token, accountId = 'ACC-1001') {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${GATEWAY_URL}/api/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      message,
      account_id: accountId,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data.message || data.error || `HTTP ${res.status} Error`;
    const err = new Error(errorMsg);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}
