import httpClient from './httpClient';

export async function fetchStudents(signal) {
  const response = await httpClient.get('/students', { signal });
  return response.data;
}

export async function fetchStudentScores(studentId) {
  const response = await httpClient.get(`/scores/by-student/${studentId}`);
  return response.data;
}

export async function createStudent(payload) {
  const response = await httpClient.post('/students', payload);
  return response.data;
}
