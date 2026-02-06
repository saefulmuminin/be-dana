from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from hashlib import sha256
import base64

pkey = RSA.importKey('-----BEGIN RSA PRIVATE KEY-----\n'+
'MIIEpAIBAAKCAQEArLJzGeuEerX7wOX/fbNhwf4ZN7rEZfzxDOBIpc+USTFvBSv7\n'+
'V76h3XW2RXG43EvcRhtBVw13uTcscVS1E+3L366SSEl9WvCvkvlxPHcvGTpDUFVU\n'+
'v9ZImBgJm0DxWTiwaQZ7nPEOeL6zb7gkWz+CuYKPJQAWC9MPQQG9RdlKYepWyIZ8\n'+
'1g+leI1CaUZnug+j+JGNlUwNplhMTqGgjDxymwCVPJGg+pMQsNwbSvSSGE7OS+bD\n'+
'OgaL1Z1YRjlYcP1C1h0PydJcLmg8+gaLcFV+WqY5594D7wjQ5Xch8rJPDmPNbjiz\n'+
'DVcOG9tC5yhwhkCci1qnxegsEEtxW8b+3jN6zwIDAQABAoIBAEMcZdZgy+7T4a2o\n'+
's4yptQeqMyqRDdmEXjhewFyPOlTnPPmJifcjQcvJ/rcl5mzVnhgwZ0fpF+mGI2M3\n'+
'Q9cmxd96+6XTyT8Z4WEARpz0w/zNw3LodjLGlxdj3/fRWPkPKp7lwgvPMYyCr0Bv\n'+
'EtHS8H4e2nnKesbFklv0zRTjyCAcR5x61i5bjvXESTZrgXMHfBjUiFPLNuTZUN4E\n'+
'AVLrKsQe+oRMCtvwLp6IvSDMH7FagV5Qq2lrw7HDaFFB1yvySk5vjh4pVCWDxjYB\n'+
'FtxqwalCfCnJyl2O/4lhTblJT862xeeeUixqgo32ZYLoYd+erEkttCbkXvILyDhY\n'+
's6blQ0ECgYEA9R5hFW7PweHFcvzoVn77oNKzyBA0BawZe8im58rohl0qn3p3YW4i\n'+
'vHEfdKvSrTghnAzVF/i1CQQ3JGq7BkN7G32sIIwl4l6YdN9swPNh8S4tqr9rXtT7\n'+
'F9QUnyjmGR4TDyHWZubjs9/gm3HGOsi947v47IL5fiY4MG5tvxr0sdcCgYEAtF0L\n'+
'SFnsZ8b/JVGz6UeIdiM/GhKWiV0xh2SZOcBHCh9r6CKdVSPegvuXivvWgBnur846\n'+
'D1mxO8GbVfJPO+KMGjsH6E7ZCuQykuRJpipuAIdB8YCaU/hOUzgOSRrdh3BPP9zO\n'+
'b+g+NXCZ1xdR1nLrqfmeodgtOTVbKWeR0h8Rz8kCgYBbZ9u+OVdiLoYJ7kPZ1XqS\n'+
'K2B9b4VmxBmwrk+HSoRRbraxR+LywzZS3UBkqppim/b0kVh5mvYviZHik6ZwnINw\n'+
'6flhHcIW2z2w/4w3m8rfPGAtNzqb34JPDXgvLfo4TZ2/29dvAhTRg9/nN5M7YpZl\n'+
'MTiPQfw1zZzQeq2UQUIUewKBgQCAr04Ifhg85u9OCiAqFd6YI4e3K4H6WeKnri/g\n'+
'034cC9Uql9/XSjNNEwLJp+sgFOCG0MX+A8l/UCBrTuoXWQkLAgkfR3p12eD3iye9\n'+
'BdLcT6TOESqLNMN1fq46nI9oPcpdT0Z+853G9SLeIwZB0lawPKhg4uNJSPdU8E9L\n'+
'Mt27eQKBgQDsF9OE5NJ+IBgCTo9cKAnA6pvByZxsKMTPrxR4kOjd51RtliVpEUfz\n'+
'LBAcTNGad1MeTkEdAaArIqc/ssVVpKi2bepJhLoPWBNSV7w2t++v+V0JGyxyLDqi\n'+
'dH8NPnp10Kghj/LlGrhvPpLlVbgTcme78PBJcpLXDkTdJAmY7JYJ2w==\n'+
'-----END RSA PRIVATE KEY-----')


path = '/v1.0/hello-world'
timestamp = '1970-01-01T00:00:00+00:00'
payload = '{"foo":"bar"}'
hashedPayload = sha256(payload.encode('utf-8')).hexdigest()
data = 'POST:'+path+':'+hashedPayload+':'+timestamp;
print('string to sign : '+data)

signer = PKCS1_v1_5.new(pkey)
digest = SHA256.new()
digest.update(data.encode("utf8"))
result = base64.b64encode(signer.sign(digest))
print('signature : ' +result)
