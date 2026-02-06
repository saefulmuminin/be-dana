my.signContract
2023-01-29 23:59
Use this API to redirect the user to the authorization page. After the user completes the authorization, the app will return the authorization code which can be used to obtain the access token for the agreement payment.

Note:

Please make sure you use the Appx with 1.24.6 or higher versions in order to use this API.

Below is a diagram that illustrates how the interaction works:

my.signContract

The merchant Mini Program server can call authorization consult API in step 2 to get the sign content with an authorization URL. Then the Mini Program will call the my.signContract JSAPI to invoke the authorization process. After the user completes the authorization, the Mini Program sends JSAPI result to its server so that the server can call apply token API to get accessToken.

Sample code
my.signContract({
  signStr: '<https://openauth.xxx.com/authentication.htm?authId=FBF16F91-28FB-47EC-B9BE-27B285C23CD3>',
  success: (res) => {
    my.alert({
    content: JSON.stringify(res),
  });
  },
  fail: (res) => {
    my.alert({
    content: JSON.stringify(res),
  });
  }
});
Parameters
Property Type 
Required

Description
signStr String Yes This parameter is the authorization string returned by the app to further the authorization process.
success Function No Callback function upon call success.
fail Function No Callback function upon call failure.
complete Function No Callback function upon call completion (to be executed upon either call success or failure).
Success Callback Function
Property Type Description
authState String  The authorization status. It is generated in Mini Program server and sent to app server. The maximum length is 256. Refer here for details.
authCode String The authorization code assigned by app which can be used to obtain the access token for the agreement payment. The maximum length is 32.
An example of a successfully returned message is as follows:

{
 "authState":"663A8FA9-D836-48EE-8AA1-1FF682989DC7",
 "authCode":"663A8FA9D83648EE8AA11FF682989DC7"
}
Fail Callback Function
Property Type Description
error String The error code for the failure.
errMessage String The error message.
Error Code
When error happens, the fail callback function will be executed. The error code can refer to the following table.

Error Code Description
6001 User cancels the sign process.
6002 The sign fails because of network error.
7001 The result of the sign is unknown, it may be successful.
7002 The sign fails.
