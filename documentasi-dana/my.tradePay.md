my.tradePay
2023-01-29 23:59
Start a payment transaction.

Sample Code
my.tradePay({
  tradeNO: '201711152100110410533667792', // get the tradeNo from the server first
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
Property

Type

Required

Description

tradeNO

String

No

The trade number. Its maximum length is 64. Refer

here

 for details.

orderStr

String

No

A string of complete payment parameters, which is recommended to be obtained from the server. Refer

here

 for details.

paymentUrl

String

No

The url of payment page. Refer

here

 for details.

success

Function

No

Callback function upon call success.

fail

Function

No

Callback function upon call failure.

complete

Function

No

Callback function upon call completion (to be executed upon either call success or failure).

The tradeNO, orderStr and paymentUrl are different ways to start the payment transaction. The Mini Program should use either one of them to start a payment transaction according to the payment service provided by the host app.

Success Callback Function
The incoming parameter is of the Object type with the following attributes:

Property

Type

Required

Description

resultCode

String

Yes

The result code of the pay process.

An example of a successfully returned message is as follows:

{
    "resultCode":"9000"
}
Result Code
resultCode

Description

9000

Payment is successful.

8000

Trade is processing.

4000

Payment is failed.

6001

User cancels to pay.

6002

Network exception.

6004

Unknown pay result, may be success.
