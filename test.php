<?php

// GSM numarasını al
$gsm = $_GET['gsm'] ?? null;

if (!$gsm) {
    echo json_encode([
        "error" => "GSM parametresi eksik. Lütfen bir telefon numarası girin."
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    exit;
}

// Türkiye ülke kodu ekle (eğer yoksa)
if (substr($gsm, 0, 2) !== '90') {
    $gsm = '90' . $gsm;
}

// cURL isteğini başlat
$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL => "https://whatsapp-data1.p.rapidapi.com/number/" . urlencode($gsm),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => "GET",
    CURLOPT_HTTPHEADER => [
        "x-rapidapi-host: whatsapp-data1.p.rapidapi.com",
        "x-rapidapi-key: 45c304bd92msh438121a532aac83p1b99a6jsnf2135eb8db18"
    ],
]);

$response = curl_exec($curl);
$error = curl_error($curl);
curl_close($curl);

if ($error) {
    echo json_encode(["error" => "cURL Hatası: " . $error], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    exit;
}

// JSON yanıtını işle
$data = json_decode($response, true);

if (!is_array($data)) {
    echo json_encode(["error" => "API'den geçerli bir JSON verisi alınamadı."], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    exit;
}

// Profil fotoğrafını base64'e çevir
$profilePhotoUrl = $data['profilePic'] ?? null;
$base64Photo = null;

if ($profilePhotoUrl) {
    try {
        $imageContent = @file_get_contents($profilePhotoUrl);
        if ($imageContent) {
            $base64Photo = base64_encode($imageContent);
        } else {
            $base64Photo = "Veri Bulunamadı";
        }
    } catch (Exception $e) {
        $base64Photo = "Hata: " . $e->getMessage();
    }
}

// JSON formatında çıktı ver
$responseData = [
    "data" => [
        "Hakkimda"    => $data['about'] ?? "",
        "UlkeKodu"    => $data['countryCode'] ?? "",
        "TelefonNo"   => $data['phone'] ?? "",
        "ProfilFoto"  => $base64Photo,
    ]
];

header('Content-Type: application/json');
echo json_encode($responseData, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);

?>
