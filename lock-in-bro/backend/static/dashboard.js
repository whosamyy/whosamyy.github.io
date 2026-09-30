fetch('/api/health').then(response => {
  if (!response.ok) throw Error('Health check failed.');
  return response.json();
}).then(data => {
  document.getElementById('health').textContent = `Backend status: ${data.status}`;
}).catch(() => {
  document.getElementById('health').textContent = 'Cannot reach the backend. Try refreshing.';
});
