import { useEffect, useState } from 'react';
import { jwtDecode } from "jwt-decode";

const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    if (token) {
      try {
        const decoded = jwtDecode(token); // Decode the token
        console.log(decoded)
        // Check if the token is valid and the username matches
        const isTokenValid = decoded.exp * 1000 > Date.now(); // Check token expiration
        const isUsernameMatch = decoded.sub === username; // Compare usernames
        console.log(isTokenValid, isUsernameMatch)

        setIsAuthenticated(isTokenValid && isUsernameMatch);
      } catch (error) {
        // If token is invalid or error in decoding, set isAuthenticated to false
        setIsAuthenticated(false);
      }
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  return isAuthenticated;
};

export default useAuth;