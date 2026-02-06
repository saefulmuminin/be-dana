my.getAuthCode
2025-05-27 23:45
Specification
The following table is a specification of this JSAPI:

JSAPI Name

my.getAuthCode

Description

This JSAPI is used to obtain the authorization code (authCode)

Request
The following part describe about parameter of request in this JSAPI:

Request Parameter
The following table is a request parameter in this JSAPI:

Name

Type

Required

Condition

Remarks

scopes

Array of String

Mandatory

-

The scope of authorization. Please refer to the Scopes Description for more information

success

Function

Optional

-

Callback function upon call success

fail

Function

Optional

-

Callback function upon call failure

complete

Function

Optional

-

Callback function upon call completion (to be executed upon either call success or failure)

Scopes Description
The following table is data of scopes in this JSAPI:

No.

Scope

Description

USER_LOGIN_ID

Authorized to obtain users' phone numbers

KYC_INFO

Authorized to obtain users' KYC information

USER_CONTACTINFO_EMAIL

Authorized to obtain users' email information

USER_BIOLOGICAL_MOTHER_NAME

Authorized to obtain users' biological mother’s name information

USER_EDUCATION_LEVEL

Authorized to obtain users' education level information

USER_OCCUPATION

Authorized to obtain users' occupation information

USER_MONTHLY_INCOME

Authorized to obtain users' monthly income information

USER_INCOME_SOURCE

Authorized to obtain users' source of income information

INVESTMENT_PURPOSE

Authorized to obtain users' purpose of investment information

USER_INVESTING_EXPERIENCE

Authorized to obtain users' investing experience information

USER_POSTAL_CODE

Authorized to obtain users' address postal code information

USER_OFFICE_NAME

Authorized to obtain users' office name information

EMPLOYER_BIZ_CTG

Authorized to obtain users' employer business category information

USER_JOB

Authorized to obtain users' job status information

USER_WORKING_EXPERIENCE

Authorized to obtain users' working experience information

USER_OFFICE_ADDRESS

Authorized to obtain users' office address information

USER_OFFICE_PROVINCE

Authorized to obtain users' office province information

USER_OFFICE_REGENCY

Authorized to obtain users' office regency information

USER_OFFICE_DISTRICT

Authorized to obtain users' office district information

USER_OFFICE_VILLAGE

Authorized to obtain users' office village information

USER_OFFICE_POSTAL_CODE

Authorized to obtain users' office postal code information

USER_BANK_NAME

Authorized to obtain users' bank name information

USER_BANK_ACCOUNT_NUMBER

Authorized to obtain users' bank account number information

USER_ACCOUNT_HOLDER_NAME

Authorized to obtain users' account holder name information

SUBSCRIPTION

Authorized to enable users to use the Subscription with Static Amount - Mini Program solution

Request Sample
The following part will be described samples of request in this JSAPI.

my.getAuthCode({
  scopes: ['USER_LOGIN_ID'],
  success: (res) => {
    my.alert({
      content: res.authCode,
    });
  },
  fail: (res) => {
      console.log(res.authErrorScopes)
  },
});
Response
The following part describe about parameter of response in this JSAPI:

Response Parameter
The following table is a response parameter in this JSAPI:

Name

Type

Required

Condition

Remarks

authCode

String

Conditional

Y:= Authorization success

Authorization code

authErrorScopes

Key-value

Conditional

Y:= Authorization failed

The scope that failed to grant authorization, key is the scope and value is the error

authSuccessScopes

Array

Conditional

Y:= Authorization success

The scope that succeed to grant authorization

Response Sample
The following part will be described samples of response in this JSAPI.

Success
The following script is a response sample of this JSAPI for success scenario:

{
    "authCode":"1591797390204",
    "authSuccessScopes":['USER_LOGIN_ID']
}
Failed
The following script is a response sample of this JSAPI for failed scenario:

{
    "authErrorScopes":{
       "USER_LOGIN_ID":"40006"
    }
}
Error Code Information
The following table shows the error codes and messages used in this JSAPI:

No.

Error Code

Error Message

3

Unknown Error

10

Empty Data

11

Unauthorized to Get User Info
