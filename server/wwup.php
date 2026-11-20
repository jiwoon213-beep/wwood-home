<?php
// 방문자 공간 사진 받기 — www.wwood.co.kr 사진찾기에서 올림. 이 파일을 서버 /www/home/wwup.php 에 올리세요.
// 저장: /www/home/wwup_data/ (웹에서 직접 못 보게 .htaccess 로 막음). 홈페이지 빌드 봇이 key 로 가져가고 처리 뒤 지웁니다.
$KEY = 'WWUP_KEY_HERE';
$DIR = dirname(__FILE__) . '/wwup_data';
header('Access-Control-Allow-Origin: https://www.wwood.co.kr');
header('Access-Control-Allow-Methods: POST, GET');
header('Content-Type: application/json; charset=utf-8');
if (!is_dir($DIR)) { @mkdir($DIR, 0755); @file_put_contents($DIR . '/.htaccess', "Deny from all\n"); @file_put_contents($DIR . '/index.html', ''); }
function out($a) { echo json_encode($a); exit; }
function okid($s) { return preg_match('/^[0-9a-z]{10,40}$/', $s); }
$k = isset($_GET['key']) ? $_GET['key'] : '';
if ($k !== '' ) {
  if ($k !== $KEY) out(array('ok' => 0, 'e' => 'key'));
  if (isset($_GET['list'])) { $L = array(); foreach (glob($DIR . '/*.json') as $f) { $L[] = basename($f, '.json'); } sort($L); out(array('ok' => 1, 'ids' => $L)); }
  $id = isset($_GET['id']) ? $_GET['id'] : '';
  if (!okid($id)) out(array('ok' => 0, 'e' => 'id'));
  if (isset($_GET['meta'])) { header('Content-Type: application/json; charset=utf-8'); readfile($DIR . "/$id.json"); exit; }
  if (isset($_GET['img'])) { header('Content-Type: image/jpeg'); readfile($DIR . "/$id.jpg"); exit; }
  if (isset($_GET['del'])) { @unlink($DIR . "/$id.jpg"); @unlink($DIR . "/$id.json"); out(array('ok' => 1)); }
  out(array('ok' => 0));
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(array('ok' => 0, 'e' => 'method'));
if (!empty($_POST['website'])) out(array('ok' => 1)); // 스팸 봇 함정
if (empty($_POST['agree'])) out(array('ok' => 0, 'e' => 'agree'));
// 같은 IP 1시간 6장까지
$ip = $_SERVER['REMOTE_ADDR']; $lg = $DIR . '/.rate'; $now = time(); $R = array();
if (is_file($lg)) { foreach (file($lg) as $ln) { $p = explode(' ', trim($ln)); if (count($p) == 2 && $now - intval($p[1]) < 3600) $R[] = $p; } }
$c = 0; foreach ($R as $p) if ($p[0] === md5($ip)) $c++;
if ($c >= 6) out(array('ok' => 0, 'e' => 'rate'));
if (!isset($_FILES['photo']) || $_FILES['photo']['error'] != 0) out(array('ok' => 0, 'e' => 'file'));
if ($_FILES['photo']['size'] > 4000000) out(array('ok' => 0, 'e' => 'size'));
$info = @getimagesize($_FILES['photo']['tmp_name']);
if (!$info || $info[2] != IMAGETYPE_JPEG || $info[0] < 300 || $info[1] < 300) out(array('ok' => 0, 'e' => 'type'));
$im = @imagecreatefromjpeg($_FILES['photo']['tmp_name']);
if (!$im) out(array('ok' => 0, 'e' => 'img'));
$id = date('ymdHis') . substr(md5(uniqid(mt_rand(), true)), 0, 8);
imagejpeg($im, "$DIR/$id.jpg", 88); imagedestroy($im); // 다시 저장해서 위치정보(EXIF) 제거
$meta = isset($_POST['meta']) ? $_POST['meta'] : '{}';
if (strlen($meta) > 20000) $meta = '{}';
$title = isset($_POST['title']) ? strip_tags(stripslashes($_POST['title'])) : ''; $title = function_exists('mb_substr') ? mb_substr($title, 0, 60, 'UTF-8') : substr($title, 0, 180);
$m = json_decode($meta, true); if (!is_array($m)) $m = json_decode(stripslashes($meta), true); if (!is_array($m)) $m = array();
$m['title'] = $title; $m['t'] = $now;
file_put_contents("$DIR/$id.json", json_encode($m));
$R[] = array(md5($ip), $now); $s = ''; foreach ($R as $p) $s .= $p[0] . ' ' . $p[1] . "\n"; file_put_contents($lg, $s);
out(array('ok' => 1, 'id' => $id));
