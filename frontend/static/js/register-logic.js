async function registerAndLogin(email, password, name) {
          try {
            // Попытка регистрации
            const registerResponse = await fetch('http://176.109.110.111/auth/register', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                email: email,
                password: password,
                nickname: name,
                role_id: 1,
                pathfile: "string",
                "is_active": true,
                "is_superuser": false,
                "is_verified": false,
              })
            });

            if (!registerResponse.ok) {
              throw new Error(`Ошибка регистрации: ${registerResponse.statusText}`);
            }

            // Попытка входа после успешной регистрации
            const loginResponse = await fetch('http://176.109.110.111/auth/jwt/login', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
              },
              body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
            });

            if (!loginResponse.ok) {
              throw new Error(`Ошибка входа: ${loginResponse.statusText}`);
            }

            const loginData = await loginResponse.json();
            // Сохранение токена в localStorage
            localStorage.setItem("auth_token", loginData.access_token);

            return loginData;

          } catch (error) {
            console.error('Ошибка:', error);
            throw error;
          }
        }

        document.getElementById('registrationForm').addEventListener('submit', async (event) => {
          event.preventDefault();
          const email = document.getElementById('email').value;
          const password = document.getElementById('password').value;
          const name = document.getElementById('nickname').value;

          try {
            await registerAndLogin(email, password, name);
            // Действия после успешной регистрации и входа
            console.log('Успешная регистрация и вход');
          } catch (error) {
            // Обработать ошибку
            console.error('Ошибка при регистрации и входе:', error);
          }
        });

        async function fetchGoogleAuthUrl() {
          try {
            const response = await fetch('http://176.109.110.111/auth/google/authorize');
            if (!response.ok) {
              throw new Error(`Ошибка запроса: ${response.statusText}`);
            }
            const data = await response.json();
            return data.authorization_url;
          } catch (error) {
            console.error('Ошибка при получении URL для Google Auth:', error);
          }
        }

        window.onload = async () => {
          const googleAuthUrl = await fetchGoogleAuthUrl();
          if (googleAuthUrl) {
            const googleAuthButton = document.getElementById('googleAuth');
            googleAuthButton.href = googleAuthUrl;
            // Если вы хотите сделать элемент ссылкой
            // googleAuthButton.onclick = () => window.location.href = googleAuthUrl;
          }
        };