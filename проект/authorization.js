async googleAuth(): Promise <void> {
    const googleAuthListener: any;
        const DIALOG = "width=600, height=679,scrollbars=1,toolbar=0,location=1"
        window.removeEventListener("message", googleAuthListener);
        const subject = new Subject<void>();
        const dialogUrl = this.buildUri("https://accounts.google.com/o/oauth2/v2/auth",{
            gsiwebsdk: 3,
            client_id: "ВАШ id",
            scope: "Email profile",
            redirect_uri:'storagerelay://${window.location.origin.replace("://","/")}?id=googAuth',
            prompt: "consent",
            acess_type: "offline",
            response_type: "code",
            include_granted_scopes: true,
            enable_serial_consent: true,
            service: "lso",
            o2v: 2,
            slowName: "GeneralOAuthFlow"
        }),
        
        googleAuthListener = async (ev: any) => {
            window.removeEventListener("message", googleAuthListener);

            const token = JSON.parse(ev.data).params.authResult.code;
            //Вот тут мы сохрангяем токен и его используем в теории
            subject.next();
            subject.complete();
        }
        window.addEventListenner("messange", googleAuthListener);

        window.open(dialogUrl,"Google Auth", DIALOG);
        return lastValueFrom(subject.asObservable());
}
const button = document.querySelector("button");
button.addEventListener("click", async (event) => {
    await googleAuth();
})