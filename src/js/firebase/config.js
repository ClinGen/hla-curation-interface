import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyD_TLzPJT3IxX59b_7raOyLka11kLYGYg0",
  authDomain: "som-clingen-projects.firebaseapp.com",
  projectId: "som-clingen-projects",
  storageBucket: "som-clingen-projects.firebasestorage.app",
  messagingSenderId: "653902215137",
  appId: "1:653902215137:web:d054a272e88ab9ca2644a0",
};
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
