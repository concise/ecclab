/*
 * ECDSA with SHA-256 on NIST P-256 using the WebCrypto API with JavaScript
 *
 * Message
 *
 *    The 6-byte ASCII string "sample"
 *
 * Secret key
 *
 *    x = c9afa9d845ba75166b5c215767b1d6934e50c3db36e89b127b8a622b120f6721
 *
 * Public key point (Ux, Uy)
 *
 *    Ux = 60fed4ba255a9d31c961eb74c6356d68c049b8923b61fa6ce669622e60f29fb6
 *    Uy = 7903fe1008b8bc99a41ae9e95628bc64f2f1b20c2d7e9f5177a3c294d4462299
 *
 * The selected ephemeral secret key k this time
 *
 *    k = a6e3c57dd01abe90086538398355dd4c3b17aa873382b0f24d6129493d8aad60
 *
 * An example signature (r, s)
 *
 *    r = efd48b2aacb6a8fd1140dd9cd45e81d69d2c877b56aaf991c34d0ea84eaf3716
 *    s = f7cb1c942d657c41d436c7a1b6e29f65f3e900dbb9aff4064dc4ab2f843acda8
 */

var GLOBAL = window;

var publicKey = undefined;

var isValidSig = undefined;

var jwkPubkey = {
  kty: 'EC',
  crv: 'P-256',
  ext: true,
  x: 'YP7UuiVanTHJYet0xjVtaMBJuJI7Yfps5mliLmDyn7Y',
  y: 'eQP-EAi4vJmkGunpVii8ZPLxsgwtfp9Rd6PClNRGIpk'};

var signature = new Uint8Array([
  0xef, 0xd4, 0x8b, 0x2a, 0xac, 0xb6, 0xa8, 0xfd, 0x11, 0x40, 0xdd, 0x9c,
  0xd4, 0x5e, 0x81, 0xd6, 0x9d, 0x2c, 0x87, 0x7b, 0x56, 0xaa, 0xf9, 0x91,
  0xc3, 0x4d, 0x0e, 0xa8, 0x4e, 0xaf, 0x37, 0x16, 0xf7, 0xcb, 0x1c, 0x94,
  0x2d, 0x65, 0x7c, 0x41, 0xd4, 0x36, 0xc7, 0xa1, 0xb6, 0xe2, 0x9f, 0x65,
  0xf3, 0xe9, 0x00, 0xdb, 0xb9, 0xaf, 0xf4, 0x06, 0x4d, 0xc4, 0xab, 0x2f,
  0x84, 0x3a, 0xcd, 0xa8]);

var data = new Uint8Array([0x73, 0x61, 0x6d, 0x70, 0x6c, 0x65]);

var tryImportingThePublicKeyAndThenVerifyingASignature = function () {
  console.log('ENTERING tryImportingThePublicKeyAndThenVerifyingASignature');
  GLOBAL.crypto.subtle.importKey(
    'jwk', jwkPubkey, {name: 'ECDSA', namedCurve: 'P-256'}, true, ['verify']
  ).then(function (pk) {
    publicKey = pk;
    console.log('The public key was successfully imported:');
    console.log(pk);
    tryVerifyingAnEcdsaSignature();
  }, function (err) {
    publicKey = null;
    console.error('Error occurred when importing a public key:');
    console.error(err);
  });
  console.log('LEAVING tryImportingThePublicKeyAndThenVerifyingASignature');
}

var tryVerifyingAnEcdsaSignature = function () {
  console.log('ENTERING tryVerifyingAnEcdsaSignature');
  GLOBAL.crypto.subtle.verify(
    {name: 'ECDSA', hash: {name: 'SHA-256'}}, publicKey, signature, data
  ).then(function (validity) {
    console.log('The result of signature verification is:');
    console.log(validity);
  }, function (err) {
    console.error('Error occurred when verifying a signature:');
    console.error(err);
  });
  console.log('LEAVING tryVerifyingAnEcdsaSignature');
};

//
// Web Cryptography API
// W3C Candidate Recommendation 11 December 2014
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/
//
// 14.3.11. The wrapKey method
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#SubtleCrypto-method-wrapKey
//
// 14.3.12. The unwrapKey method
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#SubtleCrypto-method-unwrapKey
//
// 23. ECDSA
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#ecdsa
//
// 28. AES-GCM
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#aes-gcm
//
// 33. SHA
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#sha
//
// 34. Concat KDF
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#concatkdf
//
// 35. HKDF-CTR
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#hkdf-ctr
//
// 36. PBKDF2
// http://www.w3.org/TR/2014/CR-WebCryptoAPI-20141211/#pbkdf2
//
// https://datatracker.ietf.org/wg/jose/documents/
// Javascript Object Signing and Encryption (JOSE)
// JSON Web Key (JWK)
// JSON Web Signature (JWS)
// JSON Web Encryption (JWE)
// JSON Web Algorithms (JWA)
