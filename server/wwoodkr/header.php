<? 
	include "../../common/ezs_config/config2.php";
	if(!function_exists("ww_seofix")){ function ww_seofix($b){ if(stripos($b,'<html')===false) return $b; $b=preg_replace('/<html(?![^>]*\blang=)/i','<html lang="ko"',$b,1); $p=preg_split('/(<script\b.*?<\/script>|<textarea\b.*?<\/textarea>|<style\b.*?<\/style>)/is',$b,-1,PREG_SPLIT_DELIM_CAPTURE); if(!$p) return $b; $sp=(isset($_SERVER['PHP_SELF'])&&strpos($_SERVER['PHP_SELF'],'shoplist.php')!==false); $h1=(stripos($b,'<h1')!==false); for($k=0;$k<count($p);$k+=2){ $p[$k]=preg_replace('/<img(?![^>]*\balt=)(?=[\s>\/])/i','<img alt=""',$p[$k]); if($sp && !$h1 && preg_match('/<h2\b/i',$p[$k])){ $n=0; $p[$k]=preg_replace('/<h2\b([^>]*)>(.*?)<\/h2>/is','<h1$1>$2</h1>',$p[$k],1,$n); if($n) $h1=true; } } return implode('',$p); } } /* 2026-11-20 검색 최적화: lang=ko, 상품·분류 페이지 첫 제목 h1, 사진 alt 비어 있으면 alt="" */ if(!function_exists("ww_lazy")){ function ww_lazy_cb($m){ static $i=0; $i++; return ($i<=8)?$m[0]:'<img loading="lazy" '; } function ww_lazy($b){ return ww_seofix(preg_replace_callback('/<img(?![^>]*\sloading=)\s+/i','ww_lazy_cb',$b)); } ob_start("ww_lazy"); } /* 사진 지연 로딩: 화면에 보일 때 불러와 페이지 속도 개선 */
	/* 휴대폰으로 PC 화면에 들어오면 같은 내용의 모바일 화면으로 바로 이동 (PC버전 버튼 누르면 하루 동안 PC 화면 유지) */
	if(isset($_GET['pc']) && $_GET['pc']=='1'){ @setcookie('wwpc','1',time()+86400,'/'); $_COOKIE['wwpc']='1'; }
	$ww_ua = isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '';
	if(empty($_COOKIE['wwpc']) && preg_match('/iPhone|iPod|Android.*Mobile|Mobile Safari|IEMobile|Windows Phone|SamsungBrowser.*Mobile|lgtelecom/i',$ww_ua)){
		$ww_self = basename($_SERVER['PHP_SELF']); $ww_dir = basename(dirname($_SERVER['PHP_SELF']));
		$ww_g = array(); foreach(array('idx','pmode','depth','code1_idx','code2_idx','icons','page') as $k){ if(isset($_GET[$k]) && $_GET[$k]!=='') $ww_g[$k]=$_GET[$k]; }
		$ww_to = '/home/mobile/main.php';
		if($ww_dir=='mall' && $ww_self=='shoplist.php'){
			if(!empty($ww_g['idx']) && isset($ww_g['pmode']) && $ww_g['pmode']=='view'){ $ww_to = '/home/mobile/shoplist.php?idx='.intval($ww_g['idx']).'&pmode=view'; }
			else if(!empty($ww_g['code2_idx'])){ $ww_to = '/home/mobile/shoplist.php?depth=1&code1_idx='.intval($ww_g['code1_idx']).'&code2_idx='.intval($ww_g['code2_idx']); }
			else if(!empty($ww_g['code1_idx'])){ $ww_to = (intval($ww_g['code1_idx'])==39 ? '/home/mobile/shoplist.php' : '/home/mobile/shop.php').'?depth=1&code1_idx='.intval($ww_g['code1_idx']); }
			else if(!empty($ww_g['icons'])){ $ww_to = '/home/mobile/main.php'; }
		}else if($ww_dir=='mall' && $ww_self=='info.php'){ $ww_to = '/home/mobile/info.php'; }
		else if($ww_dir=='sub05' && $ww_self=='video.php'){ $ww_to = '/home/mobile/video.php'; }
		else if($ww_dir=='sub05' && $ww_self=='menu01.php'){ $ww_to = '/home/mobile/menu04.php'; }
		else if($ww_dir=='sub06' && $ww_self=='menu01.php'){ $ww_to = '/home/mobile/menu05.php'; }
		else if($ww_dir=='sub03'){ $ww_to = '/home/mobile/customer.php'; }
		else if($ww_dir=='sub01'){ $ww_to = '/home/mobile/menu01.php'; }
		else if($ww_dir=='sub02'){ $ww_to = '/home/mobile/menu07.php'; }
		else if($ww_dir=='login'){ $ww_to = '/home/mobile/login.php'; }
		else if($ww_dir=='mall' && $ww_self=='cart.php'){ $ww_to = '/home/mobile/cart.php'; }
		if(!headers_sent()){ header('Location: '.$ww_to, true, 302); exit; }
		else { echo '<script>location.replace("'.$ww_to.'");</script>'; }
	}
if($_SERVER['PHP_SELF']=="/home/mall/index.php"){
    include "../../LOGSCRIPT/log3rdscript.php"; //로그 3차스크립트
}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<?
/* SEO: 상품·카테고리별 제목/설명 (2026-11-10 추가) */
$seo_site = "영진종합목재(월드건축자재)";
$seo_title = "영진종합목재(월드건축자재) | 대전 목재·합판·건축자재 쇼핑몰";
$seo_desc = "대전 유성 영진종합목재(월드건축자재) 쇼핑몰. 합판·집성판·방부목·데크·각재·사이딩·몰딩 등 건축자재, 원하는 사이즈 재단, 전국 용달 배송.";
$seo_canon = ""; $seo_img = "https://www.wwood.co.kr/assets/store/storefront.jpg";
if(!function_exists('seo_cut')){
	function seo_cut($t,$n){ $t=trim(preg_replace('/\s+/u',' ',strip_tags(stripslashes($t)))); if(preg_match('/^.{0,'.$n.'}/su',$t,$m)) return $m[0]; return $t; }
	function seo_h($t){ return htmlspecialchars($t, ENT_QUOTES, 'UTF-8'); }
}
if(basename($_SERVER['PHP_SELF'])=="shoplist.php"){
	$seo_pm = isset($_GET['pmode']) ? $_GET['pmode'] : (isset($pmode)?$pmode:'');
	$seo_idx = intval(isset($_GET['idx']) ? $_GET['idx'] : (isset($idx)?$idx:0));
	$seo_c1 = intval(isset($_GET['code1_idx']) ? $_GET['code1_idx'] : (isset($code1_idx)?$code1_idx:0));
	$seo_c2 = intval(isset($_GET['code2_idx']) ? $_GET['code2_idx'] : (isset($code2_idx)?$code2_idx:0)); $seo_c3 = intval(isset($_GET['code3_idx']) ? $_GET['code3_idx'] : 0); $seo_pg = intval(isset($_GET['page']) ? $_GET['page'] : 1); /* 2026-11-12 분류 페이지 대표주소(canonical) */
	if($seo_pm=="view" && $seo_idx){
		$seo_rs = @mysql_fetch_array(@mysql_query("select * from goodsdata where idx='".$seo_idx."'"));
		if($seo_rs && $seo_rs['gname']){
			$seo_n = seo_cut($seo_rs['gname'],60);
			@include_once(dirname(__FILE__)."/../../common/ezs_mall/ww_desc.php"); $seo_kw = function_exists("ww_kw") ? ww_kw($seo_rs) : ""; $seo_title = $seo_n.($seo_kw!==""?" ".$seo_kw:"")." 규격·주문 | ".$seo_site;
			$seo_cat=""; if(preg_match_all("/\d+/",$seo_rs['ctid1'],$seo_m)){ foreach($seo_m[0] as $seo_ci){ $seo_cr=@mysql_fetch_array(@mysql_query("select code1_name from code1 where idx='".intval($seo_ci)."'")); if($seo_cr && $seo_cr['code1_name'] && !preg_match("/매출|세일|베스트|신상/u",$seo_cr['code1_name'])){ $seo_cat=seo_cut($seo_cr['code1_name'],20); break; } } } $seo_desc = $seo_n.($seo_cat?" (".$seo_cat.")":"")." 규격 안내 - 대전 유성 영진종합목재(월드건축자재) 3000평 매장에서 실물 확인, 원하는 사이즈 재단, 대전·세종 배송·전국 용달. 문의 042-545-2900";
			if($seo_kw!==""){ $seo_desc = $seo_n." ".$seo_kw.substr($seo_desc, strlen($seo_n)); } $seo_canon = "https://wwood.kr/home/mall/shoplist.php?idx=".$seo_idx."&pmode=view";
			if($seo_rs['file2']){ $seo_img="https://wwood.kr/common/ezs_data/product/".$seo_rs['file2']; }else if($seo_rs['uid'] && $seo_rs['uid']==$seo_rs['file1']){ $seo_img="https://wwood.kr/modules/shop/files/".date("Y/m/d/",$seo_rs['remktime']).$seo_rs['file1']."_1.".$seo_rs['ext']; }else if($seo_rs['file1']){ $seo_img="https://wwood.kr/common/ezs_data/product/".$seo_rs['file1']; }
		}
	}else if($seo_c2){
		$seo_rs = @mysql_fetch_array(@mysql_query("select * from code2 where idx='".$seo_c2."'"));
		if($seo_rs && $seo_rs['code2_name']){ $seo_n=seo_cut($seo_rs['code2_name'],40); $seo_title=$seo_n." 종류·규격 | ".$seo_site; $seo_desc=$seo_n." 상품 모음 - 대전 유성 영진종합목재(월드건축자재). 원하는 사이즈 재단, 전국 용달 배송."; } if($seo_c1){ $seo_canon="https://wwood.kr/home/mall/shoplist.php?depth=2&code1_idx=".$seo_c1."&code2_idx=".$seo_c2.($seo_c3?"&code3_idx=".$seo_c3:"").($seo_pg>1?"&page=".$seo_pg:""); }
	}else if($seo_c1){
		$seo_rs = @mysql_fetch_array(@mysql_query("select * from code1 where idx='".$seo_c1."'"));
		if($seo_rs && $seo_rs['code1_name']){ $seo_n=seo_cut($seo_rs['code1_name'],40); $seo_title=$seo_n." 종류·규격 | ".$seo_site; $seo_desc=$seo_n." 상품 모음 - 대전 유성 영진종합목재(월드건축자재). 원하는 사이즈 재단, 전국 용달 배송."; } $seo_canon="https://wwood.kr/home/mall/shoplist.php?depth=1&code1_idx=".$seo_c1.($seo_pg>1?"&page=".$seo_pg:"");
	}
}
if(basename($_SERVER['PHP_SELF'])=="info.php"){ $seo_title = "소식·자재정보 — 목재 철물·자재 고르는 법·시공 요령 | ".$seo_site; $seo_desc = "장선걸이·기둥받침·주춧돌·정자 철물 등 목재 철물 규격과 데크·합판·오일스테인 자재 정보 글 모음. 대전 유성 영진종합목재(월드건축자재)."; $seo_canon = "https://wwood.kr/home/mall/info.php"; }
if(basename($_SERVER['PHP_SELF'])=="video.php"){
		$seo_title = "시공영상 1,200여 편 — 데크·온실·싱크대·외벽·인테리어 | ".$seo_site;
		$seo_desc = "월드건축자재DIY·월드도어 유튜브 시공·DIY 영상을 분류별로 모았습니다. 데크, 목조 온실, 원목가구, 싱크대, 외벽 사이딩, 바닥, 문 교체. 영상 속 자재는 대전 유성 매장에서 재단해 드립니다.";
		$seo_canon = "https://wwood.kr/home/sub05/video.php";
}
$seo_desc = seo_cut($seo_desc,150);
?>
<?
$ww_rd_c1 = intval(isset($_GET['code1_idx'])?$_GET['code1_idx']:0); $ww_rd_c2 = intval(isset($_GET['code2_idx'])?$_GET['code2_idx']:0); $ww_rd_idx = intval(isset($_GET['idx'])?$_GET['idx']:0);
$ww_rd_map = array(58=>"https://www.wwood.co.kr/", 54=>"https://www.wwood.co.kr/sigong.html", 59=>"https://www.wwood.co.kr/sigong.html");
if(isset($ww_rd_map[$ww_rd_c1]) && !$ww_rd_idx && in_array(basename($_SERVER['PHP_SELF']), array("shoplist.php","shop.php"))){ ?><meta http-equiv="refresh" content="0;url=<?=$ww_rd_map[$ww_rd_c1]?>"><script>location.replace("<?=$ww_rd_map[$ww_rd_c1]?>");</script><? } ?>
<title><?=seo_h($seo_title)?></title>
<meta name="naver-site-verification" content="900a6aa3f02e3a5a8750821511c83e55390de6d2"/>
<meta name="robots" content="ALL" />
<meta name="generator" content="kimsQ-RB 1.2.1" /> 
<meta name="author" content="<?=$homepage_address2?>" /> 
<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1, user-scalable=no" />
<meta name="title" content="<?=seo_h($seo_title)?>" /> 
<meta name="subject" content="월드건축자재" /> 
<meta name="keywords" content="영진종합목재,월드건축자재,영진목재,대전 목재,합판,집성판,방부목,데크,각재,사이딩,건축자재" /> 
<meta name="description" content="<?=seo_h($seo_desc)?>" />
<? if($seo_canon){ ?><link rel="canonical" href="<?=seo_h($seo_canon)?>" />
<? } ?><meta property="og:title" content="<?=seo_h($seo_title)?>" />
<meta property="og:description" content="<?=seo_h($seo_desc)?>" />
<meta property="og:site_name" content="영진종합목재(월드건축자재)" />
<meta property="og:type" content="website" />
<meta property="og:image" content="<?=seo_h($seo_img)?>" />
<? if($seo_canon){ ?><meta property="og:url" content="<?=seo_h($seo_canon)?>" /><? } ?>
<meta name="classification" content="" />
<meta name="reply-to" content="" />
<meta name="content-language" content="" />
<meta name="build" content="" />
<meta name="copyright" content="Copyrights © 2015 <?=$homepage_address2?> All Rights Reserved" />
<meta name="naver-site-verification" content="900a6aa3f02e3a5a8750821511c83e55390de6d2"/>

<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/sys.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/main_default.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/main.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/theme.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/home_default.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/home_style.css" />

<!-- Global site tag (gtag.js) - Google Analytics -->
<script>
  gtag('config', 'UA-173612578-1');
</script>

<script type="text/javascript" src="../js/jquery-1.11.0.js"></script>
<script type="text/javascript" src="../../common/ezs_js/ezssoft.js"></script>
<script type="text/javascript" src="../js/main_default.js"></script>
<script type="text/javascript" src="../js/sys.js"></script>
<script src="../js/common.js" type="text/javascript"></script>
<!--commmenu-->

<link href="../css/jquery.jdMenu.css" rel="stylesheet" type="text/css" />
<script src="../js/jquery.min.js" type="text/javascript"></script>
<script src="../js/jquery.positionBy.min.js" type="text/javascript"></script>
<script src="../js/jquery.bgiframe.min.js" type="text/javascript"></script>
<script src="../js/jquery.jdMenu.js" type="text/javascript"></script>
<script src="../js/layer_menu.js" type="text/javascript"></script>



<script type="text/javascript"> 
$(document).ready(function() {
	$('ul.jd_menu').jdMenu();
	
	$(".imgClick").hover(function(e) {
	   
		$(this).find(".over-menu").show();
		
	},function(){
		$(this).find(".over-menu").hide();
	});
})
</script>
<!--commmenu-->
<style>
	
@import url(http://fonts.googleapis.com/earlyaccess/nanumgothic.css);
@import url(http://fonts.googleapis.com/earlyaccess/jejugothic.css);

#today
{   
	position: fixed; 
	top: 200px;    /*  부라우저 상단에서 밑으로 떨어질 거리설정  */
	left: 50%;    /*  본문 내용물이 중양정렬일경우 기준점을 중앙에 준다  */
	margin-left: 620px;    /*  본문내용물의 넓이의 1/2 값 + 본문에서 떨어질 거리  */
	border:1px solid #A5A5A5;
	background-color:#fff;
	cursor:pointer;
	z-index:33;
}
#recent_id
{
	padding: 5px;
}               

#today p{ font-family: 'Jeju Gothic', sans-serif;  width:110px; height:30px; background:linear-gradient(red, #9f0303); color:#fff; line-height:33px; text-align:left; text-indent:10px; 
	font-size:0.9em; border-bottom:1px solid #c80c13; } 
#today p span { float:right; margin-right:15px;} 
#today span.yellow{ color:yellow;}
#today p{}
</style>
<script type="text/javascript" charset="UTF-8" src="//t1.daumcdn.net/adfit/static/kp.js"></script>
<script type="text/javascript">
      kakaoPixel('9097014863360931616').pageView();
      kakaoPixel('9097014863360931616').purchase({
        total_quantity: "2", // 주문 내 상품 개수(optional)
        total_price: "300",  // 주문 총 가격(optional)
        currency: "KRW",     // 주문 가격의 화폐 단위(optional, 기본 값은 KRW)
        products: [          // 주문 내 상품 정보(optional)
            { name: "snack1", quantity: "1", price: "200"},
            { name: "snack2", quantity: "1", price: "100"}
        ]
    });
</script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-6EC3G8PSDX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-6EC3G8PSDX');
</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"HardwareStore","name":"영진종합목재(월드건축자재)","alternateName":["영진종합목재","영진목재","월드건축자재","영진우드"],"telephone":"+82-42-545-2900","faxNumber":"+82-42-545-2902","email":"yjwood2021@naver.com","address":{"@type":"PostalAddress","streetAddress":"유성대로 44, 1층","addressLocality":"대전 유성구","addressCountry":"KR"},"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"07:00","closes":"18:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":["Saturday","Sunday"],"opens":"07:00","closes":"15:00"}],"url":"https://wwood.kr/home/mall/","image":"https://www.wwood.co.kr/assets/store/storefront.jpg","sameAs":["https://www.wwood.co.kr/","https://www.youtube.com/@월드건축자재DIY","https://pf.kakao.com/_JxhxoxeX"],"areaServed":["대전","세종","공주","계룡","논산","금산","옥천"]}</script>
<style>iframe[src*="youtube.com/embed"],iframe[src*="youtube-nocookie.com/embed"]{width:100%!important;max-width:880px;height:auto!important;aspect-ratio:16/9;display:block;margin:12px auto;border:0;border-radius:8px;background:#000}</style>
<script>(function(){function cands(s){var c=[],a=s;if(/^http:\/\//i.test(a))c.push(a.replace(/^http:/i,'https:'));if(/ezshosting\.com/i.test(a))c.push(a.replace(/https?:\/\/[^\/]*ezshosting\.com/i,'https://wwood.kr'));if(/%(?!25)[0-9A-F]{2}/i.test(a))c.push(a.replace(/%/g,'%25'));if(/%25/i.test(a))c.push(a.replace(/%25/gi,'%'));if(/[^\x00-\x7f]/.test(a))c.push(encodeURI(a).replace(/%25/g,'%'));return c}function fix(im){if(!im||im.tagName!='IMG'||im.__wwfix)return;var src=im.getAttribute('src')||'';if(!src||/^data:/.test(src)){return}var list=cands(src);im.__wwfix=1;var i=0;function next(){if(i<list.length){im.src=list[i++];}else{im.style.display='none';var p=im.parentNode;if(p&&p.tagName=='A'&&!p.textContent.replace(/\s/g,''))p.style.display='none';}}im.addEventListener('error',next);next();}window.addEventListener('error',function(e){var t=e.target;if(t&&t.tagName=='IMG')fix(t)},true);function scan(){var a=document.images;for(var k=0;k<a.length;k++){if(a[k].complete&&a[k].naturalWidth===0&&a[k].getAttribute('src'))fix(a[k])}}window.addEventListener('load',scan);document.addEventListener('DOMContentLoaded',function(){setTimeout(scan,1500)});})();</script>
<style>.wwlg{position:relative;container-type:inline-size}.wwlt{position:absolute;left:27.4%;right:0;top:0;bottom:0;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1;font-family:'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif;white-space:nowrap}.wwlt b{font-size:11.2cqw;font-weight:900;color:#7b7b7b;letter-spacing:-.04em}.wwlt i{font-style:normal;font-size:5.6cqw;color:#a5a5a5;margin-top:1.6cqw;font-weight:700;letter-spacing:.05em}.logo2 .wwlg{display:block;width:230px}.logo2 .wwlg img{display:block;width:230px!important;height:46px!important;max-width:none}</style><script>(function(){function h(){var a=document.querySelectorAll('img[src*="noimage"],img[src*="no_image"]');for(var i=0;i<a.length;i++){var c=a[i].closest('li')||a[i].closest('a')||a[i];c.style.display='none'}}document.addEventListener('DOMContentLoaded',h);window.addEventListener('load',h)})();</script><? $ww_pr=$_SERVER['PHP_SELF']; $ww_pc_rd=array("/home/sub01/menu01.php"=>"https://www.wwood.co.kr/price.html","/home/sub05/menu01.php"=>"https://www.wwood.co.kr/visit.html","/home/sub03/menu01.php"=>"https://www.wwood.co.kr/visit.html"); if(isset($ww_pc_rd[$ww_pr])){ ?><link rel="canonical" href="<?=$ww_pc_rd[$ww_pr]?>" /><meta http-equiv="refresh" content="0;url=<?=$ww_pc_rd[$ww_pr]?>"><script>(window.opener&&window.name!==''?window.opener.location:location).replace("<?=$ww_pc_rd[$ww_pr]?>");if(window.opener)window.close();</script><? }
$ww_alt=''; if(basename($ww_pr)=="shoplist.php" && isset($_GET['pmode']) && $_GET['pmode']=="view" && !empty($_GET['idx'])){ $ww_alt="https://wwood.kr/home/mobile/shoplist.php?idx=".intval($_GET['idx'])."&pmode=view"; } else if($ww_pr=="/home/mall/index.php"){ $ww_alt="https://wwood.kr/home/mobile/main.php"; } else if($ww_pr=="/home/sub05/video.php"){ $ww_alt="https://wwood.kr/home/mobile/video.php"; }
if($ww_alt){ ?><link rel="alternate" media="only screen and (max-width: 640px)" href="<?=$ww_alt?>" /><? } if($ww_pr=="/home/mall/index.php"){ ?><link rel="canonical" href="https://wwood.kr/home/mall/index.php" /><? } ?>
<style>img{-webkit-user-drag:none;user-drag:none;-webkit-touch-callout:none}</style><script>(function(){function blk(e){var t=e.target;if(t&&t.tagName=="IMG"){e.preventDefault();return false}}document.addEventListener("contextmenu",blk,true);document.addEventListener("dragstart",blk,true);})();</script></head>

<body onContextmenu="return false" ondragstart="return false" onselectstart="return false">
<?	include "../../home/include/setup.php"; ?>
<style>
.SLB_center { cursor:pointer; visibility:hidden; border:none; background:#fff; }
.SLB_close { cursor: pointer; display:none; font-family:Dotum,verdana,tahoma; font-size:9pt; background-color:#f87500; color:#ffffff; padding-bottom:4px; }
.SLB_caption { cursor: pointer; display:none; font-family:Dotum,verdana,tahoma; font-size:9pt; background-color:#f87500; color:#ffffff; padding-bottom:4px; }
#SLB_loading { cursor:pointer; display:none; z-index:9998; position:absolute; font-family:Dotum,verdana,tahoma; font-size:9pt; background:#000000; color:#ffffff; padding:3px 0px 4px 0px; border:solid 2px #cfcfcf; }
</style>
<div id="SLB_film" style="z-index: 9997; position:absolute; display:none; width:100%; height:100%; background-color:#000000; filter:Alpha(opacity=17); opacity:0.6; -moz-opacity:0.6;"></div>
<div id="SLB_content" onClick="SLB();" align="center" style="z-index: 9999; position:absolute;"></div>
<div id="SLB_loading" onClick="SLB();" title="로딩중...클릭시 취소" style="display:none;">&nbsp;Loading...&nbsp;</div>  
<? if($pageNum != '1' && $pageNum != '2'){//팝업일경우!! ?>
<div id="wrap">
	<div class="top_banner">
    <?
		$RollQuery = "select * from imgrolling where ctid1='H' and state='1' and hnm='1' ";
		$RollQuery.= " order by favor desc";
		$RollResult = mysql_query($RollQuery);
		$RollRs = mysql_fetch_array($RollResult);
		
		echo '<a';
		if($RollRs[urllink]){echo ' href="'.$RollRs[urllink].'"';}
		if($RollRs[tg]){echo ' target="_blank"';}
		else{echo ' target="_top"';}
		echo '>';
		echo '<img src="../../common/ezs_data/rolling/'.$RollRs[file1].'" rel="'.$i.'" />';
		echo '</a>';
	?>
    </div>
    <div class="wrapper">
        <!--head_wrap-->
        <div class="head_wrap" >		
            <!--head-->
          <div class="head">
                <!--탑메뉴-->
                <div class="topmenu">
                    <ul>
                    	<? if($memRow[idx]){?>
                        <li><a href="../../common/ezs_member/logout.php?loginOut=1" style="text-decoration:none;">로그아웃</a></li>

                        <li><a href="../../home/mall/cart.php" style="text-decoration:none;">장바구니</a></li>

                        <li><a href="../../home/sub03/menu07.php" style="text-decoration:none;">마이페이지</a></li>
						<li><a href="../sub03/menu07.php" style="text-decoration:none;"><span class="">주문/배송조회</span></a></li>
                        <? }else{?>
                        <?
							
							$Link = "../../home/login/login.php";
							if($herfUrl)
							{
								$Link.= "?herfUrl=".urlencode($herfUrl);
							}else{
								$Link.= "?herfUrl=".urlencode($_SERVER['REQUEST_URI']);
							}
							
						?>
                        <li><a href="<?=$Link?>" style="text-decoration:none;">로그인</a></li>

                        <li><a href="../../common/ezs_member/join.php" style="text-decoration:none;">회원가입</a></li>

                        <li><a href="../mall/cart.php" style="text-decoration:none;"><span class="">장바구니</span></a></li>
  
                        <li><a onclick="alert('로그인후 이용가능합니다.')" style="text-decoration:none;"><span class="">주문/배송조회</span></a></li>

                        <? }?>
                        
                    </ul>
                </div>
                <!--//탑메뉴-->
    						<!--//탑 SNS -->
    						<div class="top_sns">
                	<ul>
                		<li><a href="https://www.facebook.com/wwoodkr0425459411/?fref=ts " target="_blank"><img src="../images/comm/snsn_2.png"></a></li>
                		<li><a href="https://www.instagram.com/wwoodkr0425459411/" target="_blank"><img src="../images/comm/snsn_1.png"></a></li>
                	</ul>
                </div>
    						<!--//탑 SNS-->
    
                <!--로고2-->
                <div class="logo2">
                    <p><a href="../mall/index.php" class="wwlg"><img src="../images/mobile/yj_logo.png?v=1" alt="영진종합목재(월드건축자재)"/></a></p>
                </div>
                <!--//로고2-->
                

    
                <!--검색-->
                <div class="search" style="margin-top:20px; margin-left:170px;">
                    <form name="SearchForm" action="../../home/mall/shoplist.php" method="get" >
                        <input type="text"  name="search_keyword" class="hint hintText" size="40" value="<?=$search_keyword?>" style="margin-bottom:4px; height:30px; color:#555; font-size:1.4em; margin-top:8px; font-weight:bold; ime-mode:active;  " title="제품을 검색하세요 ex) 루바" />
                        <button style=""> 검색 </button>
					</form>
                </div>
                <!--//검색-->
                
                <!--로고-->
       

       
                <!--//로고-->
    
                <!--탑대메뉴-->
            	<div class="tmenu">   
                    <ul>
                        <li><a href="https://www.wwood.co.kr/price.html" class="one">제품단가표</a></li>
                        <li><a href="#" onClick="OpenPricePopup('../sub02/menu01.php');"  class="two" >전국운임표</a></li>
                        <li><a href="../mall/info.php" class="three">소식·자재정보</a></li>
                        <li><a href="../sub05/video.php" class="four">시공영상</a></li>
                        <li><a href="../sub06/menu03.php" target=""  class="five">도매업체 등록신청</a></li>
                        <li><a href="https://www.wwood.co.kr/visit.html" class="six" >회사소개</a></li>
                        <li class="ww7"><a href="https://www.wwood.co.kr/visit.html" target="_blank" rel="noopener" class="six">매장안내</a></li>
                        <style>.tmenu > ul > li{width:171px!important;box-sizing:border-box}.tmenu > ul > li > a{width:auto!important}</style>
                    </ul>                     
                    <!--ul>
                    	<li><a href="#" onClick="OpenPricePopup('../sub01/menu01.php');"><img src="../images/comm/tm1.jpg" class="tm1"></a></li>

                    	<li><a href="#" onClick="OpenPricePopup('../sub02/menu01.php');"><img src="../images/comm/tm2.jpg" class="tm2"></a></li>

                        <li><a href="../sub03/menu01.php"><img src="../images/comm/tm3.jpg" class="tm3"/></a></li>

                        <li><a href="http://blog.naver.com/herysot0" target="_blank"><img  src="../images/comm/tm4.jpg" class="tm4"></a></li>

                        <li><a href="../sub06/menu03.php" target=""><img src="../images/comm/tm5.jpg" class="tm5"></a></li>

                        <li><a href="../sub05/menu01.php" target=""><img src="../images/comm/tm6.jpg" class="tm6"></a></li>

                    </ul-->
              	</div>
              	<!--//탑대메뉴-->
            </div>	
            <!--//head-->
        </div>	
        <!--head_wrap-->
    
    </div>
    <!--대메뉴--> 
    <div class="menu">
        <div style="width:100%; margin:0 auto; min-width:1200px; z-index:999;">
            <ul class="jd_menu">                        
            <?
                $code1_query = "select * from code1";
				$code1_query.= " where idx ";
				$code1_query.= " order by code1_favor desc";
                $code1_result = mysql_query($code1_query);
                while($code1_rs = mysql_fetch_array($code1_result)) 
                {
                    if($code1_idx==$code1_rs[idx])
                    {
                        $code1_name = $code1_rs[code1_name];
                    }
					
					
					
					if($code1_rs[idx]=="39")
					{
						$GoDepth = "2";
					}else{
						$GoDepth = "1";
					}
            ?>
            <li class="m_top<? if($code1_rs[idx]=="59"){echo ' li-color-bg';}?>"><a class="m_top_a" href="../mall/shoplist.php?depth=<?=$GoDepth?>&code1_idx=<?=$code1_rs[idx]?>"><?=$code1_rs[code1_name]?></a><!--1차-->
            	<?
					$code2_query = "select count(*) from code2 where code1_idx='".$code1_rs[idx]."' ";
                    $code2_row = mysql_fetch_array(mysql_query($code2_query));
                  	if($code2_row[0])
					{
				?>
                <ul>
                    <!--<li><a href="../mall/shoplist.php?depth=1&code1_idx=<?=$code1_rs[idx]?>" style="text-decoration:none;">ㆍ 전체보기</a></li>
-->
                <?
					  
                    $code2_query = "select * from code2 where code1_idx='".$code1_rs[idx]."' order by code2_favor desc";
                    $code2_result = mysql_query($code2_query);
					
					
						while($code2_rs = mysql_fetch_array($code2_result)) 
						{
							if($code2_idx==$code2_rs[idx])
							{
								$code2_name = $code2_rs[code2_name];
							}
                ?>
                    <li class="m_down" ><a style="display:inline-block; width:100%; height:100%;" href="../mall/shoplist.php?depth=2&code1_idx=<?=$code1_rs[idx]?>&code2_idx=<?=$code2_rs[idx]?>">ㆍ <?=$code2_rs[code2_name]?></a><!--2차-->
                    <!--<?					
						$code3_query = "select count(idx) from code3 where code1_idx='".$code1_rs[idx]."' and code2_idx='".$code2_rs[idx]."'";
						$code3_row =mysql_fetch_array( mysql_query($code3_query));
						if($code3_row[0])
						{
					?>
                    	<ul>
                        	<li><a href="../mall/shoplist.php?depth=2&code1_idx=<?=$code1_rs[idx]?>&code2_idx=<?=$code2_rs[idx]?>" style=">ㆍ 전체보기</a></li>

							<?
                                $code3_query = "select * from code3 where code1_idx='".$code1_rs[idx]."' and code2_idx='".$code2_rs[idx]."'  order by code3_favor desc";
                                $code3_result = mysql_query($code3_query);
                                while($code3_rs = mysql_fetch_array($code3_result)) 
                                {
                                    if($code3_idx==$code3_rs[idx])
                                    {
                                        $code3_name = $code3_rs[code3_name];
                                    }
                            ?>
                            	<li><a href="../mall/shoplist.php?depth=2&code1_idx=<?=$code1_rs[idx]?>&code2_idx=<?=$code2_rs[idx]?>&code3_idx=<?=$code3_rs[idx]?>" style=" text-decoration:none;">ㆍ <?=$code3_rs[code3_name]?></a></li>

							<?
                                }
                            ?>
                		</ul>
                    <?
						}
					?>-->
                    </li>

				<?
						}
                ?>
                </ul>
                <?
					}
				?>
            </li>
			
            <?
                }
            ?>
            <!--<li class="m_top"><a class="m_top_a" target="_blank" href="https://tv.naver.com/wwood">시공영상</a>--><!--1차-->
            <!--li class="m_top"><a class="m_top_a" target="_blank" href="http://storefarm.naver.com/wwoodkr/products/643026388">목재재단</a--><!--1차-->
            </ul>
        </div>     
        <div class="admin_location"></div>               
    </div>
    <!--//대메뉴-->
<? }//팝업일경우!! ?>
<? $ww_pb2=basename($_SERVER['PHP_SELF']); if(($ww_pb2=='shop.php'||$ww_pb2=='shoplist.php') && !(isset($_GET['pmode'])&&$_GET['pmode']=='view') && !empty($_GET['code1_idx'])){ @include_once(dirname(__FILE__).'/../../common/ezs_mall/ww_desc.php'); if(function_exists('ww_cat_intro')){ $ww_c2n=''; if(!empty($_GET['code2_idx'])){ $ww_q=@mysql_fetch_array(@mysql_query("select code2_name from code2 where idx='".intval($_GET['code2_idx'])."'")); if($ww_q) $ww_c2n=trim(str_replace(',','·',strip_tags($ww_q[0]))); } echo ww_cat_intro($_GET['code1_idx'],$ww_c2n); } } ?>
<? if(in_array(basename($_SERVER['PHP_SELF']),array('shop.php','shoplist.php')) && !(isset($_GET['pmode'])&&$_GET['pmode']=='view') && (intval(isset($_GET['code1_idx'])?$_GET['code1_idx']:0)==32 || intval(isset($_GET['code2_idx'])?$_GET['code2_idx']:0)==266)){ @include(dirname(__FILE__).'/ww_chban.php'); } ?>
