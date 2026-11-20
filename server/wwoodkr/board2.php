<? include "../../common/ezs_config/config2.php"; ob_start(); ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/sys.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/main_default.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/main.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../theme.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/home_default.css" />
<link type="text/css" rel="stylesheet" charset="utf-8" href="../css/home_style.css" />
<script type="text/javascript" src="../js/jquery-1.11.0.js"></script>
<title>소식·자재 정보 | 영진종합목재(월드건축자재)</title>
<? if(isset($_GET['pmode']) && $_GET['pmode']=="view" && isset($_GET['idx'])){ ?><link rel="canonical" href="https://wwood.kr/home/mall/board2.php?pmode=view&amp;idx=<?=intval($_GET['idx'])?>" /><? } else { ?><meta name="robots" content="noindex,follow" /><? } ?>
</head>

<body onContextmenu="return false" ondragstart="return false" onselectstart="return false">
<?	include "../../home/include/setup.php"; ?>
<?	 
            
	/* ============================================================================== */
	/* =   게시판 기본 설정			          										= */
	/* = -------------------------------------------------------------------------- = */
	if( $cm == "" ) $cm = "101";
	if( $sm == "" ) $sm = "902";	
	if( $pmode == "" ) $pmode = "list";	
	
	$table_form = "1";//일반형1, 앨범형2
	//$ezs_admin = "1";//회원관리가 아닌 경우!!

	include "../../common/ezs_config/board_config.php";
	/* ============================================================================== */
	/* =   게시판 권한 설정			          										= */
	/* = -------------------------------------------------------------------------- = */
	
	//$mypagemenu ="1";
	
	//$ezs_use = "1"; //채용게시판
	$ezs_qna = "1";	//QnA게시판
	$ezs_poto = "1"; //뷰리스트게시판
	$No_editor = "1";
	if($user_session == "989")//최고관리자인 경우!!
	{
		$ezs_re ="1";  //답글 허용여부
		$ezs_notice = "1";//공지사항
	}
	
	if($_SERVER['REMOTE_ADDR'])//모든사람
	{
		$ezs_write_btn_view = "1";//쓰기버튼이보인다!!
		$ezs_write = "1";  //쓰기권한
		$ezs_edit = "1";
		$ezs_del = "1";
		$ezs_file = "1";//파일
		//$ezs_comment = "1";//댓글
		//$ezs_comment_write = "1";//댓글쓰기
		
	}
	if($_SERVER['REMOTE_ADDR'])//모든사람
	{
		$ezs_view = "1";
		$ezs_file_view = "1";
		$ezs_pwd = "1";  //비밀글 허용여부
	}

	
	/* ============================================================================== */
	/* =   게시판 기본 파일			          										= */
	/* = -------------------------------------------------------------------------- = */
	echo '<link href="../../common/ezs_board/css/ezs_board.css" rel="stylesheet" type="text/css">';
	echo '<script type="text/javascript" src="../../common/ezs_board/js/file_upload4.java"></script>';
			
	include "../../common/ezs_board/ezsboard_".$pmode.".php";	
	
?>
</body>
</html>
<? $__h=ob_get_clean(); $__ok=false;
if(preg_match('/class="txt_title">\s*([^<]+?)\s*</u',$__h,$__m)){ $__t=trim($__m[1]);
 $__b=''; $__p=strpos($__h,'thebody'); $__q=strpos($__h,'btnBox'); if($__p!==false && $__q!==false && $__q>$__p){ $__b=trim(strip_tags(substr($__h,$__p,$__q-$__p))); }
 if($__t!='' && strlen($__b)>600 && strpos($__h,'작성자</span> 관리자')!==false){ $__ok=true; $__d=trim(preg_replace('/\s+/u',' ',html_entity_decode(preg_replace('/^thebody"\s*>/','',$__b),ENT_QUOTES,'UTF-8'))); $__d=(function_exists('mb_substr')?mb_substr($__d,0,140,'UTF-8'):substr($__d,0,300)); $__te=htmlspecialchars($__t,ENT_QUOTES,'UTF-8'); $__de=htmlspecialchars($__d,ENT_QUOTES,'UTF-8'); $__id=intval($_GET['idx']); $__u='https://wwood.kr/home/mall/board2.php?pmode=view&amp;idx='.$__id; $__dt=''; if(preg_match('/작성일<\/span>\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/u',$__h,$__dm)) $__dt=$__dm[1];
 $__ld='<script type="application/ld+json">'.json_encode(array('@context'=>'https://schema.org','@type'=>'Article','headline'=>$__t,'description'=>$__d,'datePublished'=>$__dt,'author'=>array('@type'=>'Organization','name'=>'영진종합목재(월드건축자재)'),'publisher'=>array('@type'=>'Organization','name'=>'영진종합목재(월드건축자재)'),'mainEntityOfPage'=>'https://wwood.kr/home/mall/board2.php?pmode=view&idx='.$__id)).'</script>';
 $__h=preg_replace('/<title>[^<]*<\/title>/u','<title>'.$__te.'</title><meta name="description" content="'.$__de.'" /><meta name="viewport" content="width=device-width, initial-scale=1" /><meta property="og:type" content="article" /><meta property="og:title" content="'.$__te.'" /><meta property="og:description" content="'.$__de.'" /><meta property="og:url" content="'.$__u.'" />'.$__ld,$__h,1);
 $__h=preg_replace('/<html xmlns=/i','<html lang="ko" xmlns=',$__h,1);
 $__h=preg_replace('/(<th class="txt_title">)\s*([^<]+?)\s*(<\/th>)/u','$1<h1 style="font-size:20px;line-height:1.4;margin:0;font-weight:bold">$2</h1>$3',$__h,1);
 $__nav='<div style="max-width:960px;margin:0 auto;padding:10px 12px;font-size:14px;border-bottom:1px solid #ddd"><a href="/home/mall/" style="font-weight:bold;color:#c8101a">영진종합목재(월드건축자재)</a> &rsaquo; <a href="/home/mall/info.php">소식·자재정보</a> &nbsp;|&nbsp; <a href="https://www.wwood.co.kr/">자재 사진·기준가</a> &nbsp;|&nbsp; 042-545-2900</div>';
 $__h=preg_replace('/(<div id="ezsBBS">)/',$__nav.'$1',$__h,1);
 $__foot='<div style="max-width:960px;margin:16px auto;padding:12px;font-size:14px;line-height:1.8;border-top:1px solid #ddd">▶ 다른 자재 글: <a href="/home/mall/info.php">소식·자재정보 전체 보기</a> · <a href="/home/mall/">쇼핑몰 홈</a> · <a href="https://www.wwood.co.kr/gagyeok/">자재 가격 가이드</a> · <a href="https://www.wwood.co.kr/qna/">셀프 인테리어 하는 법</a><br />대전 유성대로 44, 1층 영진종합목재(월드건축자재) · 원하는 사이즈 즉석 재단 · 전국 용달 배송</div>';
 $__h=preg_replace('/<\/body>/i',$__foot.'</body>',$__h,1); } }
if(!$__ok && strpos($__h,'noindex')===false){ $__h=preg_replace('/<\/head>/i','<meta name="robots" content="noindex,follow" /></head>',$__h,1); }
echo $__h; ?>