const isAuthenticated = () => {
  const token = localStorage.getItem('token');
  return !!token; // Convert to boolean: true if token exists, false otherwise
}

export { isAuthenticated };