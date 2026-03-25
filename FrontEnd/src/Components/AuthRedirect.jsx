import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const AuthRedirect = ({ user }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!user) return;

    const checkGroups = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/v1/me/groups/",
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        );

        const data = await response.json();

        if (!response.ok) return;

        const hasGroups = data.length > 0;

        // ONLY redirect if user is in wrong place
        if (hasGroups && location.pathname !== "/dashboard") {
          navigate("/dashboard");
        }

        if (!hasGroups && location.pathname !== "/household") {
          navigate("/household");
        }

      } catch (err) {
        console.error(err);
      }
    };

    checkGroups();
  }, [user, location.pathname]);

  return null;
};

export default AuthRedirect;