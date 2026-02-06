Obtaining Testing Credentials
Visit <https://dashboard.dana.id/sandbox/>
You will receive the following credentials:
URL API Sandbox
Merchant ID
Client ID known as X-PARTNER-ID
Client Secret
Public Key
Private Key

Obtaining Production Credentials
After successfully do the sandbox, the next process is going to production, you will need to generate your own keys for the production environment. You then submit your generated Public Key so DANA can verify your requests.

The following steps are used to generate the asymmetric key used in the signature process for Production environment.

Create Private Key PKCS#1
openssl genrsa -out private_key.pem 2048

Encode Private Key to PKCS#8
openssl pkcs8 -topk8 -in rsa_private_key.pem -out pkcs8_rsa_private_key.pem -nocrypt

Generate Public Key
openssl rsa -in rsa_private_key.pem -out rsa_public_key.pem -pubout

Using the Credential
You will receive two credentials: a Private Key and a Public Key.

The Private Key is used to authenticate and communicate securely with DANA. Keep this key confidential and do not share it. The Public Key must be shared with DANA by uploading it through the Merchant Portal during form submission. After successful submission, you will receive other credentials, including Merchant ID, Client ID (also known as X-PARTNER-ID), and Client Secret.

Asymmetric Digital Signatures (X-SIGNATURE)
Skip this step if you're using DANA Library  , as it handles this automatically

SNAP APIs require a specific signature string to be generated for a field called X-SIGNATURE. This signature will be validated by DANA using your public key to confirm the authenticity of the request.

Apply Token method
Used for Apply Token API, which processes user binding to obtain an access token.

Transactional Token method
Used by most transactional APIs under the SNAP API standard.

Validating Signatures
Skip this step if you're using DANA Library  , as it handles this automatically

Here's a guideline for validating a digital signature in API requests. Follow these steps to ensure the authenticity and integrity of the request.

1. Get the Digital Signature
The digital signature is included in the HTTP header under the key X-SIGNATURE.

Example
X-SIGNATURE: iSkd8HPpdeeQSnq5lSRM46l8w/C4ZhNq7ordOv2dfDC0A0rGWxqz+9j864gcuVhu0tgTHJUuV9k5wsluig/sJ4W5Yy1EZPzbpeeUwFxSK0

1. Compose the String to Verify
Build the string that will be used to verify the digital signature:

Format
<HTTP METHOD> + ”:” + <RELATIVE PATH URL> + “:“ + LowerCase(HexEncode(SHA-256(Minify(<HTTP BODY>)))) + “:“ + <X-TIMESTAMP>

1. Verify the Signature
Use SHA-256 hashing combined with RSA-2048 encryption to verify the signature.
Compare the signature from the X-SIGNATURE header with the signature generated from the composed string using the public key of the API sender.
2. Consume the Request
If the verification is successful (the signature matches), proceed with processing the request.
If the verification fails, reject the request.
Code Example
Below are example codes that does all the authentication-related functions for each programming language:

Programming Language Method Sample Code
PHP PKCS#1 <https://www.jdoodle.com/ia/Zhc>
Java PKCS#8 <https://www.jdoodle.com/ia/XEM>
JavaScript PKCS#8 <https://www.jdoodle.com/ia/Zhj>
Go PKCS#1 <https://www.jdoodle.com/ia/Zhx>
Phyton PKCS#1 <https://ideone.com/WTe0Lw>
Support
Need help? contact our Merchant Support Team or join our Discord server
