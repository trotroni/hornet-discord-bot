const statusEl = document.getElementById("status");

function getToken() {
    return localStorage.getItem("admin_token");
}

function setToken(token) {
    localStorage.setItem("admin_token", token);
}

function clearToken() {
    localStorage.removeItem("admin_token");
}

async function checkToken() {
    let token = getToken();

    if (!token) {
        token = prompt("Entrez le token administrateur :");
        if (!token) {
            statusEl.textContent = "Aucun token fourni.";
            return;
        }
    }

    const res = await fetch("/api/admin/status", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (res.status === 200) {
        setToken(token);
        statusEl.textContent = "Token valide, accès admin autorisé.";
    } else {
        clearToken();
        alert("Token invalide");
        statusEl.textContent = "Accès refusé.";
    }
}

async function setCode() {
    const token = getToken();
    const code = document.getElementById("codeInput").value;

    if (!code) {
        alert("Entre un code HTTP");
        return;
    }

    const res = await fetch(`/api/admin/set?code=${code}`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (res.ok) {
        statusEl.textContent = `Mode forcé activé (HTTP ${code})`;
    } else {
        alert("Erreur lors de l'activation");
    }
}

async function disableMode() {
    const token = getToken();

    const res = await fetch("/api/admin/disable", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (res.ok) {
        statusEl.textContent = "Mode forcé désactivé";
    } else {
        alert("Erreur");
    }
}

function logout() {
    clearToken();
    location.reload();
}

checkToken();
