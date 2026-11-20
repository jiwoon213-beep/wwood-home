<? include "../../common/ezs_config/config2.php"; if(!function_exists("ww_seofix")){ function ww_seofix($b){ if(stripos($b,'<html')===false) return $b; $b=preg_replace('/<html(?![^>]*\blang=)/i','<html lang="ko"',$b,1); $p=preg_split('/(<script\b.*?<\/script>|<textarea\b.*?<\/textarea>|<style\b.*?<\/style>)/is',$b,-1,PREG_SPLIT_DELIM_CAPTURE); if(!$p) return $b; $sp=(isset($_SERVER['PHP_SELF'])&&strpos($_SERVER['PHP_SELF'],'shoplist.php')!==false); $h1=(stripos($b,'<h1')!==false); for($k=0;$k<count($p);$k+=2){ $p[$k]=preg_replace('/<img(?![^>]*\balt=)(?=[\s>\/])/i','<img alt=""',$p[$k]); if($sp && !$h1 && preg_match('/<h2\b/i',$p[$k])){ $n=0; $p[$k]=preg_replace('/<h2\b([^>]*)>(.*?)<\/h2>/is','<h1$1>$2</h1>',$p[$k],1,$n); if($n) $h1=true; } } return implode('',$p); } } /* 2026-11-20 검색 최적화: lang=ko, 상품·분류 페이지 첫 제목 h1, 사진 alt 비어 있으면 alt="" */ if(!function_exists("ww_lazy")){ function ww_lazy_cb($m){ static $i=0; $i++; return ($i<=8)?$m[0]:'<img loading="lazy" '; } function ww_lazy($b){ $p=preg_split('/(<script\b.*?<\/script>|<textarea\b.*?<\/textarea>)/is',$b,-1,PREG_SPLIT_DELIM_CAPTURE); if(!$p) return $b; for($k=0;$k<count($p);$k+=2){ $p[$k]=preg_replace_callback('/<img(?![^>]*\sloading=)\s+/i','ww_lazy_cb',$p[$k]); } return ww_seofix(implode('',$p)); } ob_start("ww_lazy"); } /* 사진 지연 로딩: 화면에 보일 때 불러와 페이지 속도 개선 */ ?>
<? 
if($_SERVER['PHP_SELF']=="/home/mobile/main.php"){
	include "../../LOGSCRIPT/log3rdscript.php"; //로그 3차스크립트 
}
?> 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html id="kimsQStart" lang="ko" xml:lang="ko" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,minimum-scale=1.0,user-scalable=no,target-densitydpi=medium-dpi" />
<meta name="apple-mobile-web-app-capable" content="no" />
<meta name="apple-mobile-web-app-status-bar-style" content="black" />
<?
/* SEO(모바일): 상품·카테고리별 제목/설명 (2026-11-10 추가) */
$seo_site = "영진종합목재(월드건축자재)";
$seo_title = "영진종합목재(월드건축자재) | 대전 목재·합판·건축자재 쇼핑몰";
$seo_desc = "대전 유성 영진종합목재(월드건축자재) 쇼핑몰. 합판·집성판·방부목·데크·각재·사이딩·몰딩 등 건축자재, 원하는 사이즈 재단, 전국 용달 배송.";
$seo_canon = ""; $seo_img = "https://www.wwood.co.kr/assets/store/storefront.jpg";
if(!function_exists('seo_cut')){
	function seo_cut($t,$n){ $t=trim(preg_replace('/\s+/u',' ',strip_tags(stripslashes($t)))); if(preg_match('/^.{0,'.$n.'}/su',$t,$m)) return $m[0]; return $t; }
	function seo_h($t){ return htmlspecialchars($t, ENT_QUOTES, 'UTF-8'); }
}
if(in_array(basename($_SERVER['PHP_SELF']),array("shoplist.php","shop.php"))){
	$seo_pm = isset($_GET['pmode']) ? $_GET['pmode'] : (isset($pmode)?$pmode:'');
	$seo_idx = intval(isset($_GET['idx']) ? $_GET['idx'] : (isset($idx)?$idx:0));
	$seo_c1 = intval(isset($_GET['code1_idx']) ? $_GET['code1_idx'] : (isset($code1_idx)?$code1_idx:0));
	$seo_c2 = intval(isset($_GET['code2_idx']) ? $_GET['code2_idx'] : (isset($code2_idx)?$code2_idx:0));
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
		if($seo_rs && $seo_rs['code2_name']){ $seo_n=seo_cut($seo_rs['code2_name'],40); $seo_title=$seo_n." 종류·규격 | ".$seo_site; $seo_desc=$seo_n." 상품 모음 - 대전 유성 영진종합목재(월드건축자재). 원하는 사이즈 재단, 전국 용달 배송."; }
	}else if($seo_c1){
		$seo_rs = @mysql_fetch_array(@mysql_query("select * from code1 where idx='".$seo_c1."'"));
		if($seo_rs && $seo_rs['code1_name']){ $seo_n=seo_cut($seo_rs['code1_name'],40); $seo_title=$seo_n." 종류·규격 | ".$seo_site; $seo_desc=$seo_n." 상품 모음 - 대전 유성 영진종합목재(월드건축자재). 원하는 사이즈 재단, 전국 용달 배송."; }
	}
}
if(basename($_SERVER['PHP_SELF'])=="info.php"){ $seo_title = "소식·자재정보 — 목재 철물·자재 고르는 법·시공 요령 | ".$seo_site; $seo_desc = "장선걸이·기둥받침·주춧돌·정자 철물 등 목재 철물 규격과 데크·합판·오일스테인 자재 정보 글 모음."; $seo_canon = "https://wwood.kr/home/mall/info.php"; }
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
<meta name="robots" content="ALL" />
<meta name="generator" content="kimsQ-RB 1.2.1" /> 
<meta name="author" content="wwood.kr" /> 
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
<meta name="copyright" content="Copyrights © 2015 wwood.kr All Rights Reserved" /> 
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/m_sys.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/m_main.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/m_main_add.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/jquery.bxslider.css" />

<script type="text/javascript" src="../js/jquery-1.11.0.js"></script> 
<script type="text/javascript" charset="utf-8" src="../js/sys.js"></script>
<script type="text/javascript" charset="utf-8" src="../js/m_main.js"></script>
<script type="text/javascript" charset="utf-8" src="../js/common.js"></script>
<script src="../js/common.js" type="text/javascript"></script>
<script src="../js/jquery-ui.js" type="text/javascript"></script>
<!-- Place somewhere in the <head> of your document -->    	
<script src="../js/jquery.min.js" type="text/javascript"></script>
<link rel="stylesheet" href="../css/flexslider.css" type="text/css"> 
<script src="../m_js/jquery.bxslider.js"></script>
<script src="../js/layer_menu.js" type="text/javascript"></script>

<script type="application/ld+json">{"@context":"https://schema.org","@type":"HardwareStore","name":"영진종합목재(월드건축자재)","alternateName":["영진종합목재","영진목재","월드건축자재","영진우드"],"telephone":"+82-42-545-2900","faxNumber":"+82-42-545-2902","email":"yjwood2021@naver.com","address":{"@type":"PostalAddress","streetAddress":"유성대로 44, 1층","addressLocality":"대전 유성구","addressCountry":"KR"},"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"07:00","closes":"18:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":["Saturday","Sunday"],"opens":"07:00","closes":"15:00"}],"url":"https://wwood.kr/home/mall/","image":"https://www.wwood.co.kr/assets/store/storefront.jpg","sameAs":["https://www.wwood.co.kr/","https://www.youtube.com/@월드건축자재DIY","https://pf.kakao.com/_JxhxoxeX"],"areaServed":["대전","세종","공주","계룡","논산","금산","옥천"]}</script>
<style>iframe[src*="youtube.com/embed"],iframe[src*="youtube-nocookie.com/embed"]{width:100%!important;max-width:880px;height:auto!important;aspect-ratio:16/9;display:block;margin:12px auto;border:0;border-radius:8px;background:#000}</style>
<? if(basename($_SERVER['PHP_SELF'])=="shoplist.php" && !(isset($_GET['pmode']) && $_GET['pmode']=="view")){ ?>
<style>
#contents ul.list_product_m{display:flex!important;flex-wrap:nowrap!important;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding:4px 12px 12px!important;margin:0!important}
#contents ul.list_product_m::-webkit-scrollbar{display:none}
#contents ul.list_product_m > li{flex:0 0 80%;scroll-snap-align:center;float:none!important;width:auto!important;margin:0!important;border:1px solid #e5e5e5;border-radius:10px;overflow:hidden;background:#fff;box-sizing:border-box}
#contents ul.list_product_m > li .conLeft,#contents ul.list_product_m > li .conRight{float:none!important;width:auto!important}
#contents ul.list_product_m > li .thumb img{display:block;width:100%!important;height:auto!important;aspect-ratio:4/3;object-fit:cover}
#contents ul.list_product_m > li .thumb a span{font-size:13px!important;padding:6px 0!important}
.ww_lhint{display:flex;justify-content:space-between;margin:10px 12px 6px;font-size:13px;color:#999}
.ww_lhint b{color:#222;font-size:15px}
</style>
<script>document.addEventListener('DOMContentLoaded',function(){var u=document.querySelector('#contents ul.list_product_m');if(!u)return;var n=u.children.length;var h=document.createElement('div');h.className='ww_lhint';h.innerHTML='<b>제품 '+n+'개</b><span>옆으로 밀어서 보기 ›</span>';u.parentNode.insertBefore(h,u);});</script>
<? } ?>
<script>(function(){function cands(s){var c=[],a=s;if(/^http:\/\//i.test(a))c.push(a.replace(/^http:/i,'https:'));if(/ezshosting\.com/i.test(a))c.push(a.replace(/https?:\/\/[^\/]*ezshosting\.com/i,'https://wwood.kr'));if(/%(?!25)[0-9A-F]{2}/i.test(a))c.push(a.replace(/%/g,'%25'));if(/%25/i.test(a))c.push(a.replace(/%25/gi,'%'));if(/[^\x00-\x7f]/.test(a))c.push(encodeURI(a).replace(/%25/g,'%'));return c}function fix(im){if(!im||im.tagName!='IMG'||im.__wwfix)return;var src=im.getAttribute('src')||'';if(!src||/^data:/.test(src)){return}var list=cands(src);im.__wwfix=1;var i=0;function next(){if(i<list.length){im.src=list[i++];}else{im.style.display='none';var p=im.parentNode;if(p&&p.tagName=='A'&&!p.textContent.replace(/\s/g,''))p.style.display='none';}}im.addEventListener('error',next);next();}window.addEventListener('error',function(e){var t=e.target;if(t&&t.tagName=='IMG')fix(t)},true);function scan(){var a=document.images;for(var k=0;k<a.length;k++){if(a[k].complete&&a[k].naturalWidth===0&&a[k].getAttribute('src'))fix(a[k])}}window.addEventListener('load',scan);document.addEventListener('DOMContentLoaded',function(){setTimeout(scan,1500)});})();</script>
<style>.wwlg{position:relative;container-type:inline-size}.wwlt{position:absolute;left:27.4%;right:0;top:0;bottom:0;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1;font-family:'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif;white-space:nowrap}.wwlt b{font-size:11.2cqw;font-weight:900;color:#7b7b7b;letter-spacing:-.04em}.wwlt i{font-style:normal;font-size:5.6cqw;color:#a5a5a5;margin-top:1.6cqw;font-weight:700;letter-spacing:.05em}</style><script>(function(){function h(){var a=document.querySelectorAll('img[src*="noimage"],img[src*="no_image"]');for(var i=0;i<a.length;i++){var c=a[i].closest('li')||a[i].closest('a')||a[i];c.style.display='none'}}document.addEventListener('DOMContentLoaded',h);window.addEventListener('load',h)})();</script><? $ww_pg_rd=array("menu01.php"=>"https://www.wwood.co.kr/price.html","menu04.php"=>"https://www.wwood.co.kr/visit.html","customer.php"=>"https://www.wwood.co.kr/visit.html"); $ww_pb=basename($_SERVER['PHP_SELF']); if(isset($ww_pg_rd[$ww_pb]) && dirname($_SERVER['PHP_SELF'])=="/home/mobile"){ ?><link rel="canonical" href="<?=$ww_pg_rd[$ww_pb]?>" /><meta http-equiv="refresh" content="0;url=<?=$ww_pg_rd[$ww_pb]?>"><script>location.replace("<?=$ww_pg_rd[$ww_pb]?>");</script><? } ?>
<? if($_SERVER['PHP_SELF']=="/home/mobile/main.php"){ ?><link rel="canonical" href="https://wwood.kr/home/mall/index.php" /><? } ?>
<style>img{-webkit-user-drag:none;user-drag:none;-webkit-touch-callout:none}</style><script>(function(){function blk(e){var t=e.target;if(t&&t.tagName=="IMG"){e.preventDefault();return false}}document.addEventListener("contextmenu",blk,true);document.addEventListener("dragstart",blk,true);})();</script></head>
<body>
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
<style>
	.layer_btn_2{position:fixed; z-index:9999; right:10px; bottom:140px;}
	.btn_prev{display:block;  width:50px; height:50px; background-image:url("../images/mobile/top_btn.png"); background-size:100%; margin-right:10px;}
</style>
<? if($NoTop != "1"){?>
<div class="layer_btn_2"><a href="#"class="btn_prev"></a></div>
<? }?>
<div class="layer_btn"><a href="tel:042-545-2900"><img id="EffectSrc" src="../images/mobile/p_btn.png" alt="전화걸기" /></a></div>
<script>
$(function(){
	
	Effect = function(){		
		EffectPlay = setInterval(function(){ //Set timer - this will repeat itself every 3 seconds
			$("#EffectSrc").toggleClass("on")
			if($("#EffectSrc").hasClass("on") == true)
			{
				Src = "../images/mobile/p_btn_o.png";
			}else{
				Src = "../images/mobile/p_btn.png";
			}
			$("#EffectSrc").attr("src",Src)
		}, 700); //Timer speed in milliseconds (3 seconds)
	};
	Effect()
})
</script>
<div id="wrapper">
	<!--div class="top_banner">
    <?
	/*
		$RollQuery = "select * from imgrolling where ctid1='H' and state='1' and hnm='1' ";
		$RollQuery.= " order by favor desc";
		$RollResult = mysql_query($RollQuery);
		$RollRs = mysql_fetch_array($RollResult);
		
		echo '<a';
		if($RollRs[urllink]){echo ' href="'.$RollRs[urllink].'"';}
		if($RollRs[tg]){echo ' target="_blank"';}
		else{echo ' target="_top"';}
		echo '>';
		echo '<img width="100%" height="90px" src="../../common/ezs_data/rolling/'.$RollRs[file1].'" />';
		echo '</a>';
	*/
	?>
    </div-->
	<header id="header">
		<!--loop-->
		<h1><a href="main.php" class="wwlg"><img src="../images/mobile/yj_logo.png?v=1" style="height:auto" alt="영진종합목재(월드건축자재) 대전 목재·건축자재" /></a></h1>
		<script type="text/javascript">        
		function searchChk()
		{
			
			var thisFrm = document.searchForm;
			if( !thisFrm.search_keyword.value )
			{
				alert("검색어를 입력해 주세요.");
				thisFrm.search_keyword.focus();
				return false;
			}
		
		}
		</script>
        <div id="search_wrap" class="search_wrap" style="">
			<div class="search">
				<form action="shoplist.php" name="searchForm" method="get" onsubmit="return searchChk();">
					<input type="hidden" name="mod" value="search" />
					<table>
						<tbody><tr>
							<td style="padding:0 0 0 5px;"><input type="text" name="search_keyword" class="keyword" value="제품을 검색하세요 ex) 루바" onfocus="this.value=''" ></td>
							<td style="padding:0 5px 0 0;text-align:right;">
								<input type="image" id="txt_search" src="../images/mobile/btn_search_s.png" alt="검색">					
							</td>
						</tr>
					</tbody>
					</table>
				</form>
			</div>
		</div>
		<header>
			<span class="btn"><a href="#" style="font-size:20px;">제품메뉴</a></span>
			<ul id="productMenu">
			<?
                $code1_query = "select * from code1 where idx not in ('55','54','58','59') order by FIELD(idx,23,24,53,26,25,27,31,28,29,30,32,35,37,39,22)=0, FIELD(idx,23,24,53,26,25,27,31,28,29,30,32,35,37,39,22), code1_favor desc";
                $code1_result = mysql_query($code1_query);
                while($code1_rs = mysql_fetch_array($code1_result)) 
                {
                    if($code1_idx==$code1_rs[idx])
                    {
                        $code1_name = $code1_rs[code1_name];
                    }
            ?>
                <!--loop-->
                <li>
					<a href="<?=($code1_rs[idx]=="39"?"shoplist.php":"shop.php")?>?depth=1&code1_idx=<?=$code1_rs[idx]?>"><?=str_replace(",","·",$code1_rs[code1_name])?></a>
				</li>
				<!--loop-->
			<?
                }
            ?>
            <li><a class="m_top_a" href="https://www.wwood.co.kr/cut.html">원하는 사이즈 재단</a></li>
            <li><a class="m_top_a" href="https://www.wwood.co.kr/sigong.html">시공 맡기기</a></li>
            <li><a class="m_top_a" href="/home/mobile/info.php">소식·자재정보 (목재 철물)</a></li>
            <li><a class="m_top_a" href="/home/mobile/video.php">시공영상</a><!--1차--></li>
            <li><a class="m_top_a" href="https://www.wwood.co.kr/price.html">자재 기준가</a></li>
            <li><a class="m_top_a" href="https://www.wwood.co.kr/visit.html">매장안내 (위치·영업시간)</a></li>
            
            </ul>
			<ul class="util">
            	<? if($memRow[idx]){?>
                <li><a href="logout.php?loginOut=1">로그아웃</a></li>
				<li><a href="cart.php">장바구니</a></li>
                <? }else{?>
				<li><a href="login.php">로그인</a></li>
				<li><a href="join.php">회원가입</a></li>
                <? }?>
			</ul>
		</header>
		
		<? if($PageNum == '0'){ ?>
        <script type="text/javascript" charset="utf-8">   
			$(function(){
				$('.bxSlider .slides img').each(function(){ var im=this, li=$(im).closest('li'); if(!li.find('.ww_bg').length){ $('<span class="ww_bg"></span>').css('background-image','url("'+im.src+'")').prependTo(li); } });
				(function(){var ul=$('.bxSlider .slides')[0];if(!ul)return;var n=ul.children.length,i=0,busy=0,t;
function go(k){i=(k+n)%n;var g=i*ul.clientWidth;try{ul.scrollTo({left:g,behavior:'smooth'})}catch(e){}setTimeout(function(){if(Math.abs(ul.scrollLeft-g)>2&&!busy)ul.scrollLeft=g},900);}
function arm(){clearInterval(t);if(n>1)t=setInterval(function(){if(!busy)go(i+1)},3500);}
ul.addEventListener('scroll',function(){i=Math.round(ul.scrollLeft/ul.clientWidth)},{passive:true});
ul.addEventListener('touchstart',function(){busy=1},{passive:true});
ul.addEventListener('touchend',function(){busy=0;arm()},{passive:true});
window.addEventListener('resize',function(){ul.scrollLeft=i*ul.clientWidth});arm();})();
			})
		</script>
		<style>
		.bxSlider .slides{display:flex!important;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;scrollbar-width:none;margin:0;padding:0;width:100%!important}.bxSlider .slides::-webkit-scrollbar{display:none}.bxSlider .slides li{flex:0 0 100%;width:100%!important;scroll-snap-align:start;list-style:none}.bxSlider .slides img{position:relative;z-index:1;display:block;width:100%!important;height:auto!important;aspect-ratio:2000/941;object-fit:contain}
		.bxSlider .slides li{position:relative;overflow:hidden;}
		.bxSlider .slides li .ww_bg{position:absolute;inset:-20px;background-size:cover;background-position:center;filter:blur(14px) brightness(.9);z-index:0;}
		.bx-wrapper img{position:relative;z-index:1;display:block;width:100%!important;height:auto!important;aspect-ratio:2000/941;object-fit:contain;background:transparent;}
		</style>
        <!-- 주요제품 추가(20130712)-->
		<div class="mainProduct" >
            <div class="bxSlider" style="border:1px solid #dddddd; border-top:none;">   
                <ul class="slides">  
                    <?
                        $RollQuery = "select * from imgrolling where state='1' and hnm='1' ";
                        if($PageNum=='0') $RollQuery.= " and ctid1='M'";//메인
                        if($PageNum=='10') $RollQuery.= " and ctid1='".$code1_idx."'";//서버
                        $RollQuery.= " order by favor desc";
                        $RollResult = mysql_query($RollQuery);

                        if($PageNum=='0') echo '<li><a href="https://m.youtube.com/@%EC%9B%94%EB%93%9C%EA%B1%B4%EC%B6%95%EC%9E%90%EC%9E%ACDIY?sub_confirmation=1" target="_blank" rel="noopener"><img align="top" class="photo" src="../images/mobile/yt_sub_banner.jpg?v=1" alt="유튜브 월드건축자재DIY 구독·좋아요" /></a></li>'; if($PageNum=='0') echo '<li><a href="https://www.wwood.co.kr/cut.html" target="_blank" rel="noopener"><img align="top" class="photo" src="../images/mobile/cut_banner.jpg?v=1" alt="치수만 넣으면 재단 그림 — 재단 미리보기" /></a></li>';
                        while($RollRs = mysql_fetch_array($RollResult))
                        {
							echo '<li><a';
							if($RollRs[urllink]){echo ' href="'.$RollRs[urllink].'"';}
							if($RollRs[tg]){echo ' target="_blank"';}
							else{echo ' target="_top"';}
							echo '>';
							echo '<img align="top" class="photo" src="../../common/ezs_data/rolling/'.$RollRs[file1].'" rel="'.$i.'" />';
							echo '</a></li>';
                        }
                    ?> 
                </ul> 
            </div>
		
            <? } ?>
            <?
                if($PageNum == '0')//메인제외
                {
            ?>
			<nav>
				<ul id="menu">
					<li class="m4">
                    	<a href="https://www.wwood.co.kr/price.html"><p>제품단가표</p></a>
                    </li>
                    <li class="m5">
                    	<a href="/home/mobile/info.php"><p>소식·자재정보</p></a>
                    </li>
                    <li class="m3">
                    	<a href="video.php"><p>시공영상</p></a>
                    </li>
                    <li class="m1">
						<a href="https://www.wwood.co.kr/visit.html"><p>회사소개</p></a>
                    </li>
                </ul>
            </nav>
			<?
				}
			?>
			<?
                if($PageNum != '0')//메인제외
                {
            ?>
			<div class="location_wrap">
				<div class="conLeft">
					<a href="main.php">HOME</a> > 
                    <?
					
						if($PageNum == '1'){ echo '제품단가표'; }
						else if($PageNum == '2'){ echo '오시는길'; }
						else if($PageNum == '3'){ echo '매장전경'; }
						else if($PageNum == '4'){ echo '회사소개'; }
						else if($PageNum == '5'){ echo '개인정보취급방침'; }
						else if($PageNum == '6'){ echo '이용안내'; }
						else if($PageNum == '7'){ echo '로그인'; }
						else if($PageNum == '8'){ echo '회원가입'; }
						else if($PageNum == '9'){ echo '고객센터'; }
						else if($PageNum == '11'){ echo '장바구니'; }
						else if($PageNum == '12'){ echo '주문서 작성'; }
						else if($PageNum == '13'){ echo '주문서 확인'; }
						else if($PageNum == '14'){ echo '게시판'; }
						else if($PageNum == '15'){ echo '마이페이지'; }
						else if($PageNum == '16'){ echo '전국운임표'; } else if($PageNum == '17'){ echo '시공영상'; }
						else if($search_keyword){ echo $search_keyword; }
						else 
						{
							if(!$code1_idx)
							{
								echo '상세보기';
							}else{
								$code1_query = "select * from code1 where idx='".$code1_idx."' order by code1_favor desc";
								$code1_rs = mysql_fetch_array(mysql_query($code1_query));
									
								$code2_query = "select code2_name from code2 where idx='".$code2_idx."' order by code2_favor desc";
								$code2_rs = mysql_fetch_array(mysql_query($code2_query));
								
								$code3_query = "select code3_name from code3 where idx='".$code3_idx."' order by code3_favor desc";
								$code3_rs = mysql_fetch_array(mysql_query($code3_query));
								
								$code4_query = "select code4_name from code4 where idx='".$code4_idx."' order by code4_favor desc";
								$code4_rs = mysql_fetch_array(mysql_query($code4_query));
					?>
                    <a href="shop.php?depth=1&code1_idx=<?=$code1_rs[idx]?>"><?=$code1_rs[code1_name]?></a>
                    <? if($code2_idx){ ?> > <a href="shoplist.php?depth=2&code1_idx=<?=$code1_idx?>&code2_idx=<?=$code2_idx?>"><?=$code2_rs[code2_name]?></a><? } ?>
                    <? if($code3_idx){ ?> > <a href="shoplist.php?depth=3&code1_idx=<?=$code1_idx?>&code2_idx=<?=$code2_idx?>&code3_idx=<?=$code3_idx?>"><?=$code2_rs[code3_name]?></a><? } ?>
                    <? if($code4_idx){ ?> > <a href="shoplist.php?depth=4&code1_idx=<?=$code1_idx?>&code2_idx=<?=$code2_idx?>&code3_idx=<?=$code3_idx?>&code4_idx=<?=$code4_idx?>"><?=$code2_rs[code4_name]?></a><? } ?>
					<?					
							}
						}
					?>
				</div>
			</div>
            <?
				}
			?>
			</div>
            </header>
<? $ww_pb2=basename($_SERVER['PHP_SELF']); if(($ww_pb2=='shop.php'||$ww_pb2=='shoplist.php') && !(isset($_GET['pmode'])&&$_GET['pmode']=='view') && !empty($_GET['code1_idx'])){ @include_once(dirname(__FILE__).'/../../common/ezs_mall/ww_desc.php'); if(function_exists('ww_cat_intro')){ $ww_c2n=''; if(!empty($_GET['code2_idx'])){ $ww_q=@mysql_fetch_array(@mysql_query("select code2_name from code2 where idx='".intval($_GET['code2_idx'])."'")); if($ww_q) $ww_c2n=trim(str_replace(',','·',strip_tags($ww_q[0]))); } echo ww_cat_intro($_GET['code1_idx'],$ww_c2n); } } ?>
<? if(in_array(basename($_SERVER['PHP_SELF']),array('shop.php','shoplist.php')) && !(isset($_GET['pmode'])&&$_GET['pmode']=='view') && (intval(isset($_GET['code1_idx'])?$_GET['code1_idx']:0)==32 || intval(isset($_GET['code2_idx'])?$_GET['code2_idx']:0)==266)){ @include(dirname(__FILE__).'/ww_chban.php'); } ?>
