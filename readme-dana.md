Authentication
To ensure secure and reliable communication between your system and DANA's SNAP API, Bank Indonesia mandates the use of Asymmetric Signature Authentication. This method leverages cryptographic keys to verify the identity of the sender and protect data integrity during transactions.

Overview
In the asymmetric signature scheme:

Private Key: Used by you (the merchant) to digitally sign API requests.
Public Key: Shared with DANA to verify the authenticity of your requests.
By signing your request data with your private key, you provide a secure proof that the request originates from an authorized source. This process is critical to meeting the regulatory standards mandated by Bank Indonesia.

DANA Public Key

Show Sandbox DANA Public Key

To obtain Production DANA Public Key, please contact the DANA integration team through our Discord channel .

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

Libraries
DANA libraries and testing tools provide merchants with a comprehensive integration solution that streamlines development and ensures quality. Our integrated package eliminates the need to build complex API requests from scratch while providing robust testing capabilities.

The solution handles essential DANA features including authentication, request formatting, and response parsing, with support for multiple programming languages and automated testing scenarios to validate your integration.

Supported programming languages
Golang
Golang
pkg.go.dev
GitHub
Testing script
Java
Java
Maven
GitHub
Testing script
Node.js
Node.js
npm
GitHub
Testing script
PHP
PHP
Packagist
GitHub
Testing script
Python
Python
PyPi
GitHub
Testing script
NodeJS
Python
Go
PHP

Library
Simple, efficient, and reliable - Start integrating with DANA APIs in minutes instead of hours.

DANA libraries provide a powerful toolkit that simplifies integration with DANA payment solutions. Built and maintained by our engineering team, these libraries eliminate the complexity of building API integrations from scratch.

Why you should use it
Our library simplifies your integration process by providing:

✅ Ready-to-use API client - No need to build API requests from scratch

✅ Built-in authentication handling - Secure API access out of the box

✅ Automatic request formatting - Properly structured API calls every time

✅ Response parsing - Clean, typed responses ready for your code

Requirements
Node.js version 18 or later
Your testing credentials from the merchant portal.
Installation
Install using npm or visit our Github

Install the API Library using npm
npm install dana-node@latest --save

Set up the env
Required Credentials
PRIVATE_KEY or PRIVATE_KEY_PATH        # Your private key
ORIGIN                                 # Your application's origin URL
X_PARTNER_ID                           # clientId provided during onboarding
ENV                                    # DANA's environment either 'sandbox' or 'production'

Obtaining merchant credentials: Authentication

Mandatory UAT Testing
Thorough testing is critical for ensuring your integration works correctly across all scenarios and edge cases before going live. Our standardized testing package eliminates manual configuration and significantly accelerates your integration process.

What the script does
Install the latest version of our library from Repo.
Run a complete suite of predefined test scenarios.
Display real-time test results in your terminal.
Why you should use it
Simple, automated, and reliable - get your integration tested and validated without manual effort.

Our testing package streamlines your integration process by automatically handling installation and testing. Simply clone our test suite, configure your credentials, and run the automated test script, the library will install itself and validate your integration in under 2 minutes.

The automated testing provides:

✅ Automated test scenario checklist for DANA Sandbox.

✅ Auto-installation of the latest library version.

✅ Self-running test scenarios that validate your setup.

✅ Real-time test results in your terminal.

✅ Safe testing environment - No real transactions.

Usage & Installation
Prerequisites
Node.js version 18 or later
Your testing credentials from the merchant portal.
Step 1: Clone the Test Package
Clone the test package from the provided link.

git clone <git@github.com>:dana-id/self_testing_scenario.git
cd self_testing_scenario

Step 2: Configure your environment file
Change the .env-example file name to .env and fill in your credentials. Ensure you have obtained these credentials during the onboarding process.

# Required Credentials

MERCHANT_ID=your_merchant_id        # Your unique merchant identifier
X_PARTNER_ID=your_partner_id        # Partner ID provided during onboarding
CHANNEL_ID=your_channel_id          # Channel identifier for your integration
PRIVATE_KEY=your_private_key        # Your authentication private key
ORIGIN=your_origin                  # Your application's origin URL

Step 3: Run the Automated Test Script
In your terminal, run this script your preferred programming language.

sh run-test.sh node.js

What You Get After Running the Test
🟢 Clear pass/fail status for each scenario.

🟢 Easy reruns for retesting or regression.

🟢 Testing without any real transaction, safe and isolated.

Mandatory test scenarios
By running the automated test scenario, you can execute all test scenarios simultaneously without having to run them one by one. This saves significant time since the entire test suite completes in just 2 minutes. To see the complete list of test scenarios covered in the automated testing, please refer to the section below.

Gapura Payment Gateway
Gapura Payment Gateway
Start accepting payments using a hosted checkout page or a custom API solution
Gapura Hosted Checkout
Gapura Custom Checkout
Integrated Payment Widget
Integrated Payment Widget
Gain access to millions of DANA users by using DANA accounts & payment for your business solution
DANA Widget Binding
DANA Widget Non Binding
Disbursement
Disbursement
Automate disbursement to any bank & e-wallets across Indonesia using our tailor-made APIs
Disbursement to Bank
Disbursement to DANA Balance
Merchant Management
Merchant Management
Manage accounts of multiple entities by registering them as your submerchant
Division
Shop

ANA Widget Binding
DANA Widget Binding lets you seamlessly integrate DANA payments into your platform, allowing customers to link their DANA accounts for faster, smoother transactions across all your services. Currently there are two available binding methods:

Normal Binding: Users enter their DANA-registered phone number manually.
Seamless Binding: The merchant securely passes the user's phone number (already registered on their platform) to DANA, skipping manual input.
You can initiate DANA account binding between mobile apps by using a Deeplink to open the DANA App from your mobile app for a seamless in-app experience. This flexibility helps enhance user experience while ensuring secure account linking across channels.

DANA Widget is also available for payments without account binding. Check our DANA Widget Overview  for more details

Before you start
You will need to register your business in our Merchant Portal to obtain your testing credentials. After you have created your test account, make sure you have done the following:

Finish your company registration and select Integrated Payment as your payment solution.
Setup your webhooks & redirect URLs to receive payment outcomes & redirect user after payment.
Obtain your testing credentials from the merchant portal.

User Experience
Below is a sample of the user experience for users paying using DANA Widget Binding. The checkout page is available using web browsers on mobile devices.

Mobile
User experience 1
Bind with DANA Account
Connect customer’s DANA accounts with your own!

User experience 2
Simple binding process
Just provide the customer phone number and we’ll do the rest!

User experience 3
Provide seamless payment
Linked accounts can enjoy a more seamless payment experience.

User experience 4
Pay with DANA
Customers can pay using payment methods available in their DANA Account.

User experience 5
Instant Payment Result
You & your customers instantly receive payment result.

Process Flow
The general flow of payment using the DANA Widget Binding is as follows:

Visit the DANA Widget API Overview  for edge cases and other scenarios.

Binding
Payment
DANA Widget Binding

Detailed flow explanation
NodeJS
Python
Go
PHP

Step 1 : Library Installation
Visit our Libraries & Plugins guide for detailed information on our SDK.

DANA provides server-side API libraries for several programming languages, available through common package managers, for easier installation and version management. Follow the guide below to install our library:

Requirements
Node.js version 18 or later
Your testing credentials from the merchant portal.
Installation
Install using npm or visit our Github

Install the API Library using npm
npm install dana-node@latest --save

Set up the env
Required Credentials
PRIVATE_KEY or PRIVATE_KEY_PATH        # Your private key
ORIGIN                                 # Your application's origin URL
X_PARTNER_ID                           # clientId provided during onboarding
ENV                                    # DANA's environment either 'sandbox' or 'production'

Obtaining merchant credentials: Authentication

Step 2 : Initialize the library
Visit our Authentication  guide to learn about the authentication process when not using our Library.

Follow the guide below to initialize the library

Initialize the library
import { Dana, WidgetApi as WidgetApiClient } from 'dana-node';

const danaClient = new Dana({
    partnerId: "YOUR_PARTNER_ID", // process.env.X_PARTNER_ID
    privateKey: "YOUR_PRIVATE_KEY", // process.env.X_PRIVATE_KEY
    origin: "YOUR_ORIGIN", // process.env.ORIGIN
    env: "sandbox", // process.env.DANA_ENV or process.env.ENV or "sandbox" or "production"
});
const { WidgetApi } = danaClient;

Step 3 : Bind to DANA Account
Generate a redirect URL for DANA account binding. Users will be directed to the DANA App where they can complete the binding process. Configure the OAuth URL as shown below:

Generate OAuth 2.0 URL
import { WidgetUtils } from 'dana-node/widget/v1';

// Generate OAuth URL
const oauth2UrlData = {
    redirectUrl: '<https://your-redirect-url.com>',
    externalId: 'your-external-id', // or use uuidv4()
    merchantId: process.env.MERCHANT_ID,
    seamlessData: {
        mobileNumber: '08xxxxxxxxx' // Optional
    }
};

const oauthUrl = WidgetUtils.generateOauthUrl(oauth2UrlData);
console.log(oauthUrl);

The above code redirects users to the DANA App authorization page. By providing the user's phone number in seamlessData, you can streamline the experience so users don't need to enter their number manually.

After successful authorization, the user will be redirected to your specified redirectUrl with an authCode that expires in 10 minutes. Example:

Sample response from Get OAuth 2.0 URL
<https://www.merchant.com/oauth/callback?responseCode=2001000&responseMessage=Successful&authCode=xxx&state=2345555>

Step 4 : Exchange the authCode into accessToken
After obtaining the authCode, exchange it for an accessToken using the Apply Token API. The returned accessToken and refreshToken both have a 3-year validity period. Once expired, users must rebind their DANA account.

Apply Token API
import { Dana } from 'dana-node';

const danaClient = new Dana({
    // .. initialize client with authentication
});
const { WidgetApi } = danaClient;

const request: ApplyTokenRequest = {
    // Fill in required fields here, refer to Apply Token API Detail
};

const response: ApplyTokenResponse = await WidgetApi.applyToken(request);

Step 5 : Use the Direct Debit Payment API to get a hosted checkout URL
Use the Direct Debit Payment API to create new payment requests which will then return the Checkout URL of the hosted payment page.

To create a new order, make a POST request to the Direct Debit Payment API:

Direct Debit Payment API
import { Dana } from 'dana-node';

// .. initialize client with authentication

const request: WidgetPaymentRequest = {
    // Fill in required fields here, refer to Direct Debit Payment API Detail
};

const response: WidgetPaymentResponse = await WidgetApi.widgetPayment(request);

If successful, the response will include the URL for the DANA's payment page. For example:

Sample response from Direct Debit Payment API
Content-Type: application/json
X-TIMESTAMP: 2020-12-23T08:31:11+07:00
{
  "responseCode": "2005400", // Refer to response code list
  "responseMessage": "Successful", // Refer to response code list
  "referenceNo": "2020102977770000000009", // Transaction identifier on DANA system
  "partnerReferenceNo": "2020102900000000000001", // Transaction identifier on partner system
  "webRedirectUrl": "<https://pjsp.com/universal?bizNo=REF993883&>...",
  "additionalInfo":{}
}

Step 6 : Access DANA’s page by hitting Apply OTT API
To access DANA's payment page, convert the user's access token to a one-time token (OTT) via the Apply OTT API. This token has a 10-minute expiration period and can be used only once.

Apply OTT API
import { Dana } from 'dana-node';

const danaClient = new Dana({
    // .. initialize client with authentication
});
const { WidgetApi } = danaClient;

const request: ApplyOTTRequest = {
    // Fill in required fields here, refer to Apply OTT API Detail
};

const response: ApplyOTTResponse = await WidgetApi.applyOTT(request);

Step 7 : Redirect to DANA's checkout page
Generate a payment URL by combining the webRedirectUrl from the Direct Debit Payment API with an OTT token from the Apply OTT API.

Sample webRedirectUrl
import { Util } from 'dana-node/widget/v1';
import { WidgetPaymentResponse, ApplyOTTResponse } from 'dana-node/widget/v1/models';

// Example response from createWidgetPayment
const widgetPaymentResponse = new WidgetPaymentResponse({
  webRedirectUrl: '<https://example.com/payment?token=abc123>'
}); // this should be from createPayment Widget API

// Example response from applyOTT
const applyOTTResponse = new ApplyOTTResponse({
  userResources: [
    {
      value: 'ott_token_value'
    }
  ]
}); // this should be from applyOTT Widget API

// Generate the payment URL
const paymentUrl = Util.generateCompletePaymentUrl(widgetPaymentResponse, applyOTTResponse);

Optional Query Order Status, Cancel Order, Refund Order, Balance Inquiry, and Query User Profile

Step 8 : Receive Payment Outcome
After a successful payment:

Notification: The user will be redirected to your specified Redirect URL, which you can configure using the urlParams parameter in the Direct Debit Payment API request, the redirection URL has a format like: https:xxx?originalReferenceNo=xxx&originalPartnerReferenceNo=xxx&merchantId=xxxx&status=xxx

merchant redirect URL: set on urlParams.url
originalReferenceNo: Original transaction identifier on DANA system
originalPartnerReferenceNo: Original transaction identifier on partner system
merchantId: Merchant identifier that is unique per each merchant
status: Payment transaction in DANA side
Example: <https://www.merchantUrl.com/result/?originalReferenceNo=20250613111212800100166070954004283&originalPartnerReferenceNo=8562466e47144b5f82c003b47ae3c474&merchantId=216620000020928274717&status=SUCCESS>
[Optional] Finish Notify: In case you add urlParams.type = NOTIFICATION, DANA will send payment notifications to your Notification URL via the Finish Notify API. Configure your notification endpoint with the ASPI-mandated path format: /v1.0/debit/notify.

Construction
Construction
new WebhookParser(publicKey?: string, publicKeyPath?: string)

Request
Parameter Type Remarks
publicKey string The DANA gateway's public key as a PEM formatted string. This is used if publicKeyPath is not provided or is empty
publicKeyPath string The file path to the DANA gateway's public key PEM file. If provided, this will be prioritized over the publicKey string
Notes: One of publicKey or publicKeyPath must be provided.

Method
Method
parseWebhook(httpMethod: string, relativePathUrl: string, headers: { [key: string]: string }, body: string): FinishNotifyRequest

Request
Parameter Type Remarks
httpMethod string The HTTP method of the incoming webhook request e.g., POST
relative_path_url string The relative URL path of the webhook endpoint that received the notification e.g /v1.0/debit/notify
headers map[string]string A map containing the HTTP request headers. This map must include X-SIGNATURE and X-TIMESTAMP headers provided by DANA for signature verification
body string The raw JSON string payload from the webhook request body
Returns: A pointer to a FinishNotifyRequeststruct containing the parsed and verified webhook data, or an error if parsing or signature verification fails.
Raises: ValueError if signature verification fails or the payload is invalid.
Security Notes
Always use the official public key provided by DANA for webhook verification.
Reject any webhook requests that fail signature verification or have malformed payloads.
Never trust webhook data unless it passes verification.
Webhook Finish Notify
import { WebhookParser } from 'dana-node/dist/webhook'; // Adjust import path as needed

async function handleDanaWebhook(req: AnyRequestType, res: AnyResponseType) {
    // Retrieve the DANA public key from environment variables or a secure configuration.
    // Option 1: Public key as a string
    const danaPublicKeyString: string | undefined = process.env.DANA_WEBHOOK_PUBLIC_KEY_STRING;
    // Option 2: Path to the public key file (recommended for production)
    const danaPublicKeyPath: string | undefined = process.env.DANA_WEBHOOK_PUBLIC_KEY_PATH;

    if (!danaPublicKeyString && !danaPublicKeyPath) {
        console.error('DANA webhook public key not configured.');
        res.status(500).send('Webhook processor configuration error.'); // Or appropriate error handling
        return;
    }

    const httpMethod: string = req.method!; // e.g., "POST"
    const relativePathUrl: string = req.path!; // e.g., "/v1.0/debit/notify". Ensure this is the path DANA signs.

    const headers: Record<string, string> = req.headers as Record<string, string>;

    let requestBodyString: string;
    if (typeof req.body === 'string') {
        requestBodyString = req.body;
    } else if (req.body && typeof req.body === 'object') {
        requestBodyString = JSON.stringify(req.body);
    } else {
        console.error('Request body is not a string or a parseable object.');
        res.status(400).send('Invalid request body format.');
        return;
    }

    // Initialize WebhookParser.
    const parser = new WebhookParser(danaPublicKeyString, danaPublicKeyPath);

    try {
        // Verify the signature and parse the webhook payload
        const finishNotify = parser.parseWebhook(
            httpMethod,
            relativePathUrl,
            headers,
            requestBodyString
        );

        console.log('Webhook verified successfully:');
        console.log('Original Partner Reference No:', finishNotify.originalPartnerReferenceNo);
        // TODO: Process the finishNotify object (e.g., update order status in your database)

        res.status(200).send('Webhook received and verified.');
    } catch (error: any) { // Catching as 'any' to access error.message
        console.error('Webhook verification failed:', error.message);
        // Respond with an error status. DANA might retry if it receives an error.
        res.status(400).send(`Webhook verification failed: ${error.message}`);
    }
}

For detailed example, please refer to the following resource: Example Webhook.

Example of a successful payment webhook payload:
Example of a successful Finish Notify:
Content-type: application/json
X-TIMESTAMP: 2020-12-23T07:44:16+07:00
{
  "responseCode": "2005600",
  "responseMessage": "Successful"
}

Additional Enum Configuration

Optional Revoke DANA's user account

Step 9 : Test using our automated test suite
Visit our Scenario Testing  guide for detailed information on testing requirements.

We are required by local regulators to ensure your integration works correctly across all critical use cases. Use our sandbox environment and Merchant Portal to safely conduct UAT testing on a list of mandatory testing scenarios.

Access your Integration Checklist page inside the Merchant Portal
Complete all the mandatory testing scenarios provided
Download your verified API Logs using the Download Verification Proof button
Complete your Go Live Submission checklist
Submit your verified API logs on your Production Submission form
UAT Testing Script
Use our specialized UAT testing suite to save days of debugging.

To speed up your integration, we have provided an automated test suite. It takes under 15 minutes to run your integration against our test scenarios. Check out the Github repo for more instructions

Step 10 : Submit testing documents & apply for production
As part of regulatory compliance, merchants are required to submit UAT testing documents to meet Bank Indonesia's requirements. After completing sandbox testing, follow these steps to move to production:

Generate production keys
Create your production private and public keys, follow this instruction: Authentication - Production Credential.

Complete your UAT testing checklist
Confirm that you have completed all testing scenarios from our Merchant Portal.

Fill out your Production Submission form
Follow the instructions inside our Merchant Portal to apply for production credentials. We will process your application in 1-2 days.

Obtain production credentials
Once approved, you will receive your production credentials such as: Merchant ID, Client ID known as X-PARTNER-ID, and Client Secret.

Testing in production environment

Configure production environment
Switch your application settings from sandbox to production environment by updating the API endpoints and credentials.

Test using production credentials
Conduct the same testing scenarios as sandbox testing, using your production credentials.

UAT production sign-off
Once testing is complete, DANA will prepare the UAT Production Sign Off document in the Merchant Portal. Both merchant and DANA representatives must sign this document to formally approve the integration.

Receive live payments
After receiving all approvals, your DANA integration will be activated and ready for live payments from your customers.

DANA Widget Non Binding
DANA Widget Non Binding integrates DANA as a payment method in your platform without account binding. Users simply select DANA, get redirected to the DANA App, and complete payments using their DANA account.

Before you start
You will need to register your business in our Merchant Portal to obtain your testing credentials. After you have created your test account, make sure you have done the following:

Finish your company registration and select Integrated Payment as your payment solution.
Setup your webhooks & redirect URLs to receive payment outcomes & redirect user after payment.
Obtain your testing credentials from the merchant portal.

User Experience
Mobile
User experience 1
Pay with DANA
User selects DANA as their payment method.

User experience 2
Payment Details
User reviews transaction details and completes payment in the DANA App.

User experience 3
Payment Result
User instantly receive payment result.

Process Flow
The general flow of payment using the DANA Widget Non Binding is as follows:

Visit the DANA Widget API Overview  for edge cases and other scenarios.

DANA Widget Binding

Detailed flow explanation
NodeJS
Python
Go
PHP

Step 1 : Library Installation
Visit our Libraries & Plugins guide for detailed information on our SDK.

DANA provides server-side API libraries for several programming languages, available through common package managers, for easier installation and version management. Follow the guide below to install our library:

Requirements
Node.js version 18 or later
Your testing credentials from the merchant portal.
Installation
Install using npm or visit our Github

Install the API Library using npm
npm install dana-node@latest --save

Set up the env
Required Credentials
PRIVATE_KEY or PRIVATE_KEY_PATH        # Your private key
ORIGIN                                 # Your application's origin URL
X_PARTNER_ID                           # clientId provided during onboarding
ENV                                    # DANA's environment either 'sandbox' or 'production'

Obtaining merchant credentials: Authentication

Step 2 : Initialize the library
Visit our Authentication  guide to learn about the authentication process when not using our Library.

Follow the guide below to initialize the library

Initialize the library
import { Dana, WidgetApi as WidgetApiClient } from 'dana-node';

const danaClient = new Dana({
    partnerId: "YOUR_PARTNER_ID", // process.env.X_PARTNER_ID
    privateKey: "YOUR_PRIVATE_KEY", // process.env.X_PRIVATE_KEY
    origin: "YOUR_ORIGIN", // process.env.ORIGIN
    env: "sandbox", // process.env.DANA_ENV or process.env.ENV or "sandbox" or "production"
});
const { WidgetApi } = danaClient;

Step 3 : Use the Direct Debit Payment API to get a hosted checkout URL
Use the Direct Debit Payment API to create new payment requests which will then return the Checkout URL of the hosted payment page.

To create a new order, make a POST request to the Direct Debit Payment API:

Direct Debit Payment API
import { Dana } from 'dana-node';

// .. initialize client with authentication

const request: WidgetPaymentRequest = {
    // Fill in required fields here, refer to Direct Debit Payment API Detail
};

const response: WidgetPaymentResponse = await WidgetApi.widgetPayment(request);

If successful, the response will include the URL for the DANA's payment page. For example:

Sample response from Direct Debit Payment API
Content-Type: application/json
X-TIMESTAMP: 2020-12-23T08:31:11+07:00
{
  "responseCode": "2005400", // Refer to response code list
  "responseMessage": "Successful", // Refer to response code list
  "referenceNo": "2020102977770000000009", // Transaction identifier on DANA system
  "partnerReferenceNo": "2020102900000000000001", // Transaction identifier on partner system
  "webRedirectUrl": "<https://pjsp.com/universal?bizNo=REF993883&>...",
  "additionalInfo":{}
}

Optional Query Order Status, Cancel Order, Refund Order, and Balance Inquiry

Step 4 : Receive Payment Outcome
After a successful payment:

Notification: The user will be redirected to your specified Redirect URL, which you can configure using the urlParams parameter in the Direct Debit Payment API request, the redirection URL has a format like: https:xxx?originalReferenceNo=xxx&originalPartnerReferenceNo=xxx&merchantId=xxxx&status=xxx

merchant redirect URL: set on urlParams.url
originalReferenceNo: Original transaction identifier on DANA system
originalPartnerReferenceNo: Original transaction identifier on partner system
merchantId: Merchant identifier that is unique per each merchant
status: Payment transaction in DANA side
Example: <https://www.merchantUrl.com/result/?originalReferenceNo=20250613111212800100166070954004283&originalPartnerReferenceNo=8562466e47144b5f82c003b47ae3c474&merchantId=216620000020928274717&status=SUCCESS>
[Optional] Finish Notify: In case you add urlParams.type = NOTIFICATION, DANA will send payment notifications to your Notification URL via the Finish Notify API. Configure your notification endpoint with the ASPI-mandated path format: /v1.0/debit/notify.

Construction
Construction
new WebhookParser(publicKey?: string, publicKeyPath?: string)

Request
Parameter Type Remarks
publicKey string The DANA gateway's public key as a PEM formatted string. This is used if publicKeyPath is not provided or is empty
publicKeyPath string The file path to the DANA gateway's public key PEM file. If provided, this will be prioritized over the publicKey string
Notes: One of publicKey or publicKeyPath must be provided.

Method
Method
parseWebhook(httpMethod: string, relativePathUrl: string, headers: { [key: string]: string }, body: string): FinishNotifyRequest

Request
Parameter Type Remarks
httpMethod string The HTTP method of the incoming webhook request e.g., POST
relative_path_url string The relative URL path of the webhook endpoint that received the notification e.g /v1.0/debit/notify
headers map[string]string A map containing the HTTP request headers. This map must include X-SIGNATURE and X-TIMESTAMP headers provided by DANA for signature verification
body string The raw JSON string payload from the webhook request body
Returns: A pointer to a FinishNotifyRequeststruct containing the parsed and verified webhook data, or an error if parsing or signature verification fails.
Raises: ValueError if signature verification fails or the payload is invalid.
Security Notes
Always use the official public key provided by DANA for webhook verification.
Reject any webhook requests that fail signature verification or have malformed payloads.
Never trust webhook data unless it passes verification.
Webhook Finish Notify
import { WebhookParser } from 'dana-node/dist/webhook'; // Adjust import path as needed

async function handleDanaWebhook(req: AnyRequestType, res: AnyResponseType) {
    // Retrieve the DANA public key from environment variables or a secure configuration.
    // Option 1: Public key as a string
    const danaPublicKeyString: string | undefined = process.env.DANA_WEBHOOK_PUBLIC_KEY_STRING;
    // Option 2: Path to the public key file (recommended for production)
    const danaPublicKeyPath: string | undefined = process.env.DANA_WEBHOOK_PUBLIC_KEY_PATH;

    if (!danaPublicKeyString && !danaPublicKeyPath) {
        console.error('DANA webhook public key not configured.');
        res.status(500).send('Webhook processor configuration error.'); // Or appropriate error handling
        return;
    }

    const httpMethod: string = req.method!; // e.g., "POST"
    const relativePathUrl: string = req.path!; // e.g., "/v1.0/debit/notify". Ensure this is the path DANA signs.

    const headers: Record<string, string> = req.headers as Record<string, string>;

    let requestBodyString: string;
    if (typeof req.body === 'string') {
        requestBodyString = req.body;
    } else if (req.body && typeof req.body === 'object') {
        requestBodyString = JSON.stringify(req.body);
    } else {
        console.error('Request body is not a string or a parseable object.');
        res.status(400).send('Invalid request body format.');
        return;
    }

    // Initialize WebhookParser.
    const parser = new WebhookParser(danaPublicKeyString, danaPublicKeyPath);

    try {
        // Verify the signature and parse the webhook payload
        const finishNotify = parser.parseWebhook(
            httpMethod,
            relativePathUrl,
            headers,
            requestBodyString
        );

        console.log('Webhook verified successfully:');
        console.log('Original Partner Reference No:', finishNotify.originalPartnerReferenceNo);
        // TODO: Process the finishNotify object (e.g., update order status in your database)

        res.status(200).send('Webhook received and verified.');
    } catch (error: any) { // Catching as 'any' to access error.message
        console.error('Webhook verification failed:', error.message);
        // Respond with an error status. DANA might retry if it receives an error.
        res.status(400).send(`Webhook verification failed: ${error.message}`);
    }
}

For detailed example, please refer to the following resource: Example Webhook.

Example of a successful payment webhook payload:
Example of a successful Finish Notify:
Content-type: application/json
X-TIMESTAMP: 2020-12-23T07:44:16+07:00
{
  "responseCode": "2005600",
  "responseMessage": "Successful"
}

Additional Enum Configuration

Step 5 : Test using our automated test suite
Visit our Scenario Testing  guide for detailed information on testing requirements.

We are required by local regulators to ensure your integration works correctly across all critical use cases. Use our sandbox environment and Merchant Portal to safely conduct UAT testing on a list of mandatory testing scenarios.

To complete our mandatory testing requirements, follow these steps:

Access your Integration Checklist page inside the Merchant Portal
Complete all the mandatory testing scenarios provided
Download your verified API Logs using the Download Verification Proof button
Complete your Go Live Submission checklist
Submit your verified API logs on your Production Submission form
UAT Testing Script
Use our specialized UAT testing suite to save days of debugging.

To speed up your integration, we have provided an automated test suite. It takes under 15 minutes to run your integration against our test scenarios. Check out the Github repo for more instructions

Step 6 : Submit testing documents & apply for production
As part of regulatory compliance, merchants are required to submit UAT testing documents to meet Bank Indonesia's requirements. After completing sandbox testing, follow these steps to move to production:

Generate production keys
Create your production private and public keys, follow this instruction: Authentication - Production Credential.

Complete your UAT testing checklist
Confirm that you have completed all testing scenarios from our Merchant Portal.

Fill out your Production Submission form
Follow the instructions inside our Merchant Portal to apply for production credentials. We will process your application in 1-2 days.

Obtain production credentials
Once approved, you will receive your production credentials such as: Merchant ID, Client ID known as X-PARTNER-ID, and Client Secret.

Testing in production environment

Configure production environment
Switch your application settings from sandbox to production environment by updating the API endpoints and credentials.

Test using production credentials
Conduct the same testing scenarios as sandbox testing, using your production credentials.

UAT production sign-off
Once testing is complete, DANA will prepare the UAT Production Sign Off document in the Merchant Portal. Both merchant and DANA representatives must sign this document to formally approve the integration.

Receive live payments
After receiving all approvals, your DANA integration will be activated and ready for live payments from your customers.

Disbursement
Merchant Management
Gapura Payment Gateway
Settlement File Format
