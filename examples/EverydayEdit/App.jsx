import React, {useEffect, useState} from 'react';
import {View, Text as NativeText, Platform, ScrollView, Pressable, TextInput, Image, StyleSheet, useColorScheme} from 'react-native';
import config from './src/config.json';
import ProductCard from './src/components/ProductCard';
import {loadState, saveState} from './src/storage';

function Text(props){return <NativeText {...props} style={[{fontFamily:config.bodyFont==='serif'?Platform.select({ios:'Georgia',default:'serif'}):undefined},props.style]}/>;}
export default function App(){
 const [page,setPage]=useState(config.pages[0]);
 const [cart,setCart]=useState({});
 const [ready,setReady]=useState(false);
 const [query,setQuery]=useState('');
 const [category,setCategory]=useState('All');
 const [selected,setSelected]=useState(config.products[0]);
 const [address,setAddress]=useState('');
 const [customer,setCustomer]=useState('');
 const [order,setOrder]=useState(null);
 const [orders,setOrders]=useState([]);
 const [message,setMessage]=useState('');
 const scheme=useColorScheme();
 const dark=config.theme==='dark'||(config.theme==='system'&&scheme==='dark');
 const bg=dark?'#14121d':'#fbfaf7', fg=dark?'#f6f3ff':'#221d32', muted=dark?'#b9b2c9':'#70697c';
 const total=config.products.reduce((n,p)=>n+p.price*(cart[p.id]||0),0);
 const count=Object.values(cart).reduce((a,b)=>a+b,0);
 useEffect(()=>{loadState().then(s=>{if(s){setCart(s.cart||{});setOrders(s.orders||[]);}setReady(true);}).catch(()=>{setReady(true);setMessage('Saved cart could not be loaded.');});},[]);
 useEffect(()=>{if(ready)saveState({cart,orders}).catch(()=>setMessage('Could not save on this device.'));},[cart,orders,ready]);
 function add(p){setCart(c=>({...c,[p.id]:(c[p.id]||0)+1}));setMessage(p.name+' added to bag');}
 function quantity(id,delta){setCart(c=>{const next={...c,[id]:Math.max(0,(c[id]||0)+delta)};if(!next[id])delete next[id];return next;});}
 function go(p){setPage(p);setMessage('');}
 function place(){if(!customer.trim()||address.trim().length<8){setMessage('Enter your name and a delivery address of at least 8 characters.');return;}if(!count){setMessage('Your bag is empty.');return;}const o={id:'JN-'+Date.now(),total,customer,address,items:cart,date:new Date().toISOString()};setOrders(s=>[o,...s]);setOrder(o);setCart({});setMessage('Demo order saved on this device. No payment was charged.');}
 const button=(label,onPress,secondary=false)=> <Pressable accessibilityRole="button" onPress={onPress} style={[s.button,{backgroundColor:secondary?(dark?'#302a40':config.secondary):config.primary}]}><Text style={{color:secondary?fg:'#fff',fontWeight:'700'}}>{label}</Text></Pressable>;
 const input=(placeholder,value,change)=> <TextInput accessibilityLabel={placeholder} placeholder={placeholder} placeholderTextColor={muted} value={value} onChangeText={change} style={[s.input,{color:fg,borderColor:dark?'#43394f':'#d8d1e4'}]}/>;
 const filtered=config.products.filter(p=>(category==='All'||category===p.category)&&p.name.toLowerCase().includes(query.toLowerCase()));
 const navigation=<ScrollView horizontal={config.navigation!=='sidebar'} style={[s.nav,{backgroundColor:dark?'#211c2d':'#fff'},config.navigation==='sidebar'&&{maxHeight:'100%',width:95,maxWidth:95}]} contentContainerStyle={{alignItems:'center',paddingHorizontal:config.navigation==='sidebar'?4:12,gap:4}}>{config.pages.filter(p=>p!=='detail'&&p!=='checkout').map(p=><Pressable accessibilityRole="button" key={p} onPress={()=>go(p)} style={[s.tab,page===p&&{backgroundColor:config.primary+'20'}]}><Text style={{color:page===p?config.primary:muted,fontWeight:'600',textTransform:'capitalize'}}>{p==='products'?'Shop':p}</Text></Pressable>)}</ScrollView>;
 return <View nativeID={'jinie-page-'+page} style={[s.root,{backgroundColor:bg}]}>
  <View style={s.header}><View style={{flex:1,marginRight:10}}><Text style={[s.eyebrow,{color:config.primary}]}>CURATED FOR YOU</Text><Text style={[s.brand,{color:fg,fontFamily:config.font==='serif'?Platform.select({ios:'Georgia',default:'serif'}):undefined}]}>{config.name}</Text></View>{config.pages.includes('cart')&&button('Bag · '+count,()=>go('cart'),true)}</View>
  <View style={{flex:1,flexDirection:config.navigation==='sidebar'?'row':'column'}}>
  {config.navigation!=='bottom'&&navigation}
  <ScrollView contentContainerStyle={s.content}>
   {message!==''&&<Text accessibilityRole="alert" style={[s.notice,{color:fg}]}>{message}</Text>}
   {page==='home'&&<View style={[s.hero,{backgroundColor:config.primary}]}><Text style={s.heroSmall}>A LITTLE EVERYDAY EXTRAORDINARY</Text><Text style={s.heroTitle}>Good things.{'\n'}Great discoveries.</Text><Text style={s.heroBody}>Explore our carefully chosen {config.business} collection.</Text>{config.pages.includes('products')&&button('Explore collection →',()=>go('products'),true)}</View>}
   {['home','products','search'].includes(page)&&<>
    <Text style={[s.heading,{color:fg}]}>{page==='home'?'The latest selection':page==='search'?'Find your favourite':'The collection'}</Text>
    {(page==='search'||config.features.includes('search'))&&input('Search products',query,setQuery)}
    <View style={s.row}>{['All',...new Set(config.products.map(p=>p.category))].map(c=><Pressable accessibilityRole="button" key={c} onPress={()=>setCategory(c)} style={[s.chip,{backgroundColor:category===c?config.primary:dark?'#302a40':'#eeeaf6'}]}><Text style={{color:category===c?'white':fg}}>{c}</Text></Pressable>)}</View>
    <View style={[s.grid,config.layout==='editorial'&&{flexDirection:'column'}]}>{filtered.map(p=><View key={p.id} style={{width:config.layout!=='grid'?'100%':'47%',minWidth:140,flexGrow:1}}><ProductCard horizontal={config.layout==='cards'} product={p} primary={config.primary} dark={dark} onOpen={()=>{setSelected(p);if(config.pages.includes('detail'))go('detail');}} onAdd={config.pages.includes('cart')?()=>add(p):null}/></View>)}</View>
    {filtered.length===0&&<Text style={{color:muted}}>No products match your search.</Text>}
   </>}
   {page==='detail'&&selected&&<>
    <View style={[s.art,{backgroundColor:dark?'#2c253b':'#f4effa',overflow:'hidden',position:'relative'}]}>
      {selected.image_url ? (
        <Image source={{uri:selected.image_url}} style={{width:'100%',height:'100%'}} resizeMode="cover"/>
      ) : (
        <Text style={{fontSize:90}}>{selected.icon || '✦'}</Text>
      )}
      {Boolean(selected.badge)&&<View style={[s.detailBadge,{backgroundColor:config.primary}]}><Text style={{color:'white',fontWeight:'700',fontSize:12}}>{selected.badge}</Text></View>}
    </View>
    <View style={s.detailMeta}>
      <Text style={[s.eyebrow,{color:config.primary}]}>{selected.category || 'Curated Selection'}</Text>
      {Boolean(selected.rating)&&<Text style={s.detailRating}>★ {selected.rating} Customer Rating</Text>}
    </View>
    <Text style={[s.heading,{color:fg}]}>{selected.name}</Text>
    <Text style={[s.price,{color:config.accent}]}>Rs. {selected.price.toLocaleString()}</Text>
    <Text style={[s.body,{color:muted}]}>{selected.description}</Text>
    {config.pages.includes('cart')&&button('Add to bag',()=>add(selected))}
    {button('Back to collection',()=>go(config.pages.includes('products')?'products':'home'),true)}
   </>}
   {page==='cart'&&<>
    <Text style={[s.heading,{color:fg}]}>Your bag</Text>
    {count===0&&<Text style={[s.body,{color:muted}]}>Your bag is empty. Discover something you love.</Text>}
    {config.products.filter(p=>cart[p.id]).map(p=><View key={p.id} style={s.cartRow}>
      <View style={{width:58,height:58,borderRadius:12,backgroundColor:dark?'#302a40':'#eeeaf6',alignItems:'center',justifyContent:'center',overflow:'hidden'}}>
        {p.image_url ? (
          <Image source={{uri:p.image_url}} style={{width:'100%',height:'100%'}} resizeMode="cover"/>
        ) : (
          <Text style={{fontSize:28}}>{p.icon || '✦'}</Text>
        )}
      </View>
      <View style={{flex:1}}>
        <Text style={{color:fg,fontWeight:'700'}}>{p.name}</Text>
        <Text style={{color:muted}}>Rs. {(p.price*cart[p.id]).toLocaleString()}</Text>
        <View style={s.row}>
          {button('−',()=>quantity(p.id,-1),true)}
          <Text accessibilityLabel={'Quantity '+p.name} style={{color:fg,fontWeight:'700',marginHorizontal:6}}>{cart[p.id]}</Text>
          {button('+',()=>quantity(p.id,1),true)}
        </View>
      </View>
    </View>)}
    <Text style={[s.heading,{color:fg}]}>Total · Rs. {total.toLocaleString()}</Text>
    {count>0&&config.pages.includes('checkout')&&button('Continue to checkout',()=>go('checkout'))}
   </>}
   {page==='checkout'&&<><Text style={[s.heading,{color:fg}]}>Checkout</Text>{order&&<View style={s.notice}><Text style={{color:fg}}>Order {order.id} saved · Rs. {order.total.toLocaleString()}</Text></View>}{input('Full name',customer,setCustomer)}{input('Delivery address',address,setAddress)}<Text style={[s.body,{color:muted}]}>Cash on delivery · Demo orders are stored locally on this device. This is not a live payment or fulfilment service.</Text><Text style={[s.heading,{color:fg}]}>Rs. {total.toLocaleString()}</Text>{button('Place demo order',place)}<Text style={[s.body,{color:muted}]}>{orders.length} saved order(s)</Text></>}
   {page==='contact'&&<><Text style={[s.heading,{color:fg}]}>Let's talk.</Text><Text style={[s.body,{color:muted}]}>We would love to help you find the right fit.</Text><Text style={{color:fg}}>{config.contact}</Text><Text style={[s.body,{color:muted}]}>Contact details are sample content. Edit src/config.json before publishing.</Text></>}
   {page==='about'&&<><Text style={[s.heading,{color:fg}]}>A thoughtful collection.</Text><Text style={[s.body,{color:muted}]}>{config.name} brings together carefully selected {config.business} essentials. Built with care, made for everyday life.</Text></>}
   <Text style={[s.footer,{color:muted}]}>Made with Jinie · Sample catalog</Text>
  </ScrollView>
  {config.navigation==='bottom'&&navigation}
  </View>
 </View>;
}
const s=StyleSheet.create({root:{flex:1,paddingTop:32},header:{padding:22,flexDirection:'row',justifyContent:'space-between',alignItems:'center'},eyebrow:{fontSize:9,letterSpacing:2,fontWeight:'700'},brand:{fontSize:25,fontWeight:'800',marginTop:5},content:{padding:22,paddingTop:8,paddingBottom:35},hero:{borderRadius:24,padding:26,marginBottom:24},heroSmall:{color:'#eee5ff',fontSize:9,letterSpacing:2},heroTitle:{fontSize:32,lineHeight:38,color:'white',fontWeight:'800',marginVertical:18},heroBody:{color:'#eee5ff',lineHeight:22,marginBottom:20},heading:{fontFamily:config.font==='serif'?Platform.select({ios:'Georgia',default:'serif'}):undefined,fontSize:25,fontWeight:'700',marginVertical:18},body:{fontSize:15,lineHeight:25,marginVertical:16},button:{paddingVertical:13,paddingHorizontal:17,borderRadius:13,alignItems:'center',marginVertical:5},row:{flexDirection:'row',gap:8,alignItems:'center',marginVertical:10,flexWrap:'wrap'},chip:{paddingVertical:9,paddingHorizontal:14,borderRadius:25},grid:{flexDirection:'row',flexWrap:'wrap',gap:14},input:{borderWidth:1,padding:15,borderRadius:12,marginVertical:8,fontSize:15},price:{fontSize:24,fontWeight:'700',marginVertical:12},art:{height:220,borderRadius:24,alignItems:'center',justifyContent:'center'},detailBadge:{position:'absolute',top:14,left:14,paddingHorizontal:12,paddingVertical:5,borderRadius:14},detailMeta:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginTop:14},detailRating:{fontSize:12,fontWeight:'700',color:'#eab308'},cartRow:{flexDirection:'row',gap:16,alignItems:'center',paddingVertical:16,borderBottomWidth:1,borderColor:'#bbb3ca40'},nav:{maxHeight:65,minHeight:65,borderTopWidth:1,borderColor:'#bbb3ca30'},tab:{padding:14,borderRadius:12},notice:{padding:14,backgroundColor:'#aa92e320',borderRadius:12,marginBottom:12},footer:{fontSize:11,textAlign:'center',marginTop:40}});
