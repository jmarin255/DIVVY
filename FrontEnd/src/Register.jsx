import { useState } from "react";

const Register = () => {
    const [formData, setFormData] = useState({
        firstName : "",
        lastName : "",
        email : "",
        password : "",


    });

    const [error, setError] = useState("");
    const [theme , setTheme] = useState("light");

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name] : e.target.value

        })
    };

    const handleSubmit = (e) => {
        e.preventDefualt ();
        console.log(formData);
    };

    if (!formData.email.includes("@")) {
        setError("Enter a valid email")
    }


    return (
        <div className="container d-flex justify-content-center align-items-center vh-100">
            
        </div>
    )


    






}