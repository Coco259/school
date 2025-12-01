import httpClient from './httpClient';

export async function fetchCourseScores(courseId) {
  const response = await httpClient.get(`/scores/by-course/${courseId}`);
  return response.data;
}

export async function saveScore(payload) {
  const response = await httpClient.post('/scores', payload);
  return response.data;
}
