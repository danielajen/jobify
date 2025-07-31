import React, { createContext, useState, useContext, useEffect } from 'react';
import { API_URL } from '../config';

const UserContext = createContext();

// Simplified user fields to reduce property count
const filterUserFields = (data) => {
  if (!data) return {};
  return {
    id: data.id,
    name: data.name || '',
    email: data.email || '',
    phone: data.phone || '',
    graduation_year: data.graduation_year || '',
    degree: data.degree || '',
    answers: data.answers || {},
    resume: data.resume || null,
    job_alerts: data.job_alerts !== false,
    auto_apply: data.auto_apply !== false
  };
};

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch user profile from backend
  const fetchProfile = async (userId) => {
    setLoading(true);
    setError(null);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // Reduced timeout

      const response = await fetch(`${API_URL}/profile?user_id=${userId}`, {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server returned ${response.status} status`);
      }

      const userData = await response.json();
      setUser(filterUserFields({
        id: userId,
        ...userData
      }));
    } catch (err) {
      console.error('Error fetching profile:', err);

      // Handle specific error types
      if (err.name === 'AbortError') {
        setError('Request timed out. Please check your internet connection.');
      } else if (err.message.includes('JSON')) {
        setError('Invalid response from server. Please try again.');
      } else {
        setError(`Network error: ${err.message}`);
      }

      // Simplified fallback user
      const fallbackUser = {
        id: userId,
        name: 'Daniel Ajenifuja',
        email: 'danielajeni.11@gmail.com',
        phone: '6479069726',
        graduation_year: '2027',
        degree: 'Western University Computer Science',
        answers: {
          strengths: 'Proficient in Python, React, and cloud technologies',
          why_company: 'I admire your innovative approach to change lives through technology',
        },
        resume: null,
        job_alerts: true,
        auto_apply: true
      };

      setUser(filterUserFields(fallbackUser));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const userId = 'test-user';
    fetchProfile(userId);
  }, []);

  const updateUser = async (newData) => {
    if (!newData?.id) return;

    setUser((prev) => filterUserFields({ ...prev, ...newData }));

    try {
      const response = await fetch(`${API_URL}/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: newData.id,
          ...filterUserFields(newData),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save profile');
      }
    } catch (err) {
      console.error('Update error:', err);
      // Don't throw error to prevent app crash, just log it
    }
  };

  const value = {
    user,
    loading,
    error,
    updateUser,
    refetch: () => user && fetchProfile(user.id),
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};