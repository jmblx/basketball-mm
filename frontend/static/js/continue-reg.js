 async function submitRegistration() {
            const userNickname = document.getElementById("userNickname").value;
            const phoneNumber = document.getElementById("phoneNumber").value;
            const password = document.getElementById("password").value;
            const avatar = document.getElementById("avatar").files[0];
            const formData = new FormData();
            formData.append('file', avatar);

            // Отдельный запрос для передачи фотографи

            const response = await fetch('/profile/uploadfile/user/avatar', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem("auth_token")}`
                }
            });

            const avatarResponse = await response.json();

            // Отдельный запрос для передачи остальных данных пользователя
            const data = {
                nickname: userNickname,
                phone_number: phoneNumber,
                password: password,
            };

            await fetch('/custom/final_auth_google', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem("auth_token")}`
                }
            });

            alert("Registration completed!");
            window.location = "/pages/main"
        }