import { API_BASE_URL } from '@/config';
import { store } from '@/store';
import { Auth } from '@/store/_auth';
import axios from 'axios';

export function setupAxios() {
  const state = store.getState();
  axios.defaults.baseURL = API_BASE_URL;
  axios.defaults.headers.common.Accept = 'application/json';
  axios.defaults.headers.post['Content-Type'] = 'application/json';
  axios.defaults.headers.common.Authorization = Auth.select.authorization(state);
}
