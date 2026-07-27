import { useState } from "react";
import { authService, type RegisterData } from "../services/auth";
import { useNavigate } from "react-router-dom";

interface AxiosErrorLike {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState<RegisterData>({
    email: "",
    username: "",
    password: "",
    first_name: "",
    last_name: "",
  });

  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await authService.register(form);

      authService.setToken(response.access_token);

      navigate("/dashboard");

    } catch (err: unknown) {
      const error = err as AxiosErrorLike;
      setError(
        error.response?.data?.detail || "Registration failed"
      );
    }
  };


  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">

      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">

        <h1 className="text-2xl font-bold mb-6 text-center">
          Create Account
        </h1>


        {error && (
          <p className="text-red-500 mb-4">
            {error}
          </p>
        )}


        <form onSubmit={handleSubmit} className="space-y-3">

          <input
            placeholder="First name"
            className="w-full border p-2 rounded"
            onChange={(e)=>
              setForm({...form, first_name:e.target.value})
            }
          />


          <input
            placeholder="Last name"
            className="w-full border p-2 rounded"
            onChange={(e)=>
              setForm({...form, last_name:e.target.value})
            }
          />


          <input
            placeholder="Username"
            className="w-full border p-2 rounded"
            onChange={(e)=>
              setForm({...form, username:e.target.value})
            }
          />


          <input
            type="email"
            placeholder="Email"
            className="w-full border p-2 rounded"
            onChange={(e)=>
              setForm({...form, email:e.target.value})
            }
          />


          <input
            type="password"
            placeholder="Password"
            className="w-full border p-2 rounded"
            onChange={(e)=>
              setForm({...form, password:e.target.value})
            }
          />


          <button
            className="w-full bg-blue-500 text-white p-2 rounded"
          >
            Register
          </button>

        </form>

      </div>

    </div>
  );
}