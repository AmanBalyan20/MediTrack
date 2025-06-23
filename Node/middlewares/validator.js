const axios = require("axios");


async function validator(req, res, next) {
    const token = req.headers["authorization"]?.split(" ")[1]; 
    if (!token) {
        return res.status(403).json({ error: "Authorization token is missing" });
    }
    try {
        const response = await axios.get("http://localhost:3999/auth/validate", {
           headers:{Authorization:`Bearer ${token}`}
        });
        if (response.data.valid) {
            req.user = response.data.user; 
            next(); 
        } else {
            return res.status(401).json({ error: "Invalid token" });
        }
    } catch (error) {
        return res
            .status(401)
            .json({ error: error.response?.data?.error || "Token validation failed" });
    }
}

module.exports = validator;
