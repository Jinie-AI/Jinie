import React, {useEffect, useState} from 'react';
import {View, Text as NativeText, Platform, ScrollView, Pressable, TextInput, Image, StyleSheet, useColorScheme} from 'react-native';
import config from './src/config.json';
import ProductCard from './src/components/ProductCard';
import {loadState, saveState} from './src/storage';

function Text(props){return <NativeText {...props} style={[{fontFamily:config.bodyFont==='serif'?Platform.select({ios:'Georgia',default:'serif'}):undefined},props.style]}/>;}

const TAB_LABELS = { home: 'Home', products: 'Shop', search: 'Search', cart: 'Bag', checkout: 'Checkout', contact: 'Contact', about: 'About', settings: 'Settings', profile: 'Profile' };
const TAB_ICONS = { home: '⌂', products: '🛍️', search: '🔍', cart: '🛒', checkout: '✓', contact: '📞', about: 'ⓘ', settings: '⚙️', profile: '👤' };

export default function App(){
 const initialPage = (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('page')) || config.pages[0];
 const [page,setPage]=useState(config.pages.includes(initialPage) ? initialPage : config.pages[0]);
 const [cart,setCart]=useState({});
 const [ready,setReady]=useState(false);
 const [query,setQuery]=useState('');
 const [category,setCategory]=useState('All');
 const [selected,setSelected]=useState(config.products[0]);
 const [address,setAddress]=useState('House 42, Street 8, F-7/2, Islamabad');
 const [customer,setCustomer]=useState('Ahmed Khan');
 const [order,setOrder]=useState(null);
 const [orders,setOrders]=useState([]);
 const [message,setMessage]=useState('');
 const [notifications,setNotifications]=useState(true);
 const scheme=useColorScheme();
 const dark=config.theme==='dark'||(config.theme==='system'&&scheme==='dark');
 const bg=dark?'#14121d':'#fcfaf7', fg=dark?'#f6f3ff':'#1a1824', muted=dark?'#b9b2c9':'#7a708a', cardBg=dark?'#211c2d':'#ffffff';
 const total=config.products.reduce((n,p)=>n+p.price*(cart[p.id]||0),0);
 const count=Object.values(cart).reduce((a,b)=>a+b,0);

 useEffect(()=>{loadState().then(s=>{if(s){setCart(s.cart||{});setOrders(s.orders||[]);}setReady(true);}).catch(()=>{setReady(true);setMessage('Saved cart could not be loaded.');});},[]);
 useEffect(()=>{if(ready)saveState({cart,orders}).catch(()=>setMessage('Could not save on this device.'));},[cart,orders,ready]);

 function add(p){setCart(c=>({...c,[p.id]:(c[p.id]||0)+1}));setMessage(p.name+' added to bag');}
 function quantity(id,delta){setCart(c=>{const next={...c,[id]:Math.max(0,(c[id]||0)+delta)};if(!next[id])delete next[id];return next;});}
 function go(p){setPage(p);setMessage('');}
 function place(){if(!customer.trim()||address.trim().length<8){setMessage('Enter your name and a delivery address of at least 8 characters.');return;}if(!count){setMessage('Your bag is empty.');return;}const o={id:'JN-'+Date.now(),total,customer,address,items:cart,date:new Date().toISOString()};setOrders(s=>[o,...s]);setOrder(o);setCart({});setMessage('Demo order saved on this device. No payment was charged.');}
 function clearDemoData(){setCart({});setOrders([]);setOrder(null);setMessage('Demo state and order history cleared.');}

 const button=(label,onPress,secondary=false)=> <Pressable accessibilityRole="button" onPress={onPress} style={[s.button,{backgroundColor:secondary?(dark?'#302a40':(config.secondary||'#ede5f7')):config.primary}]}><Text style={{color:secondary?(dark?'#f6f3ff':'#1a1824'):'#fff',fontWeight:'700',fontSize:11}}>{label}</Text></Pressable>;
 const input=(placeholder,value,change)=> <TextInput accessibilityLabel={placeholder} placeholder={placeholder} placeholderTextColor={muted} value={value} onChangeText={change} style={[s.input,{color:fg,borderColor:dark?'#43394f':'rgba(0,0,0,0.1)',backgroundColor:cardBg}]}/>;
 const filtered=config.products.filter(p=>(category==='All'||category===p.category)&&p.name.toLowerCase().includes(query.toLowerCase()));

 const navPages=config.pages.filter(p=>p!=='detail'&&p!=='checkout');
 const navigation=<ScrollView horizontal={config.navigation!=='sidebar'} style={[s.nav,{backgroundColor:dark?'#211c2d':'#fff'},config.navigation==='sidebar'&&{maxHeight:'100%',width:100,maxWidth:100}]} contentContainerStyle={{alignItems:'center',justify:config.navigation==='bottom'?'space-around':'flex-start',paddingHorizontal:config.navigation==='sidebar'?4:8,gap:4}}>{navPages.map(p=><Pressable accessibilityRole="button" key={p} onPress={()=>go(p)} style={[s.tab,page===p&&{backgroundColor:config.primary+'20'}]}><Text style={{fontSize:13,textAlign:'center',color:page===p?config.primary:muted}}>{TAB_ICONS[p]||'✦'}</Text><Text style={{color:page===p?config.primary:muted,fontWeight:'700',fontSize:9,textTransform:'capitalize'}}>{TAB_LABELS[p]||p}</Text></Pressable>)}</ScrollView>;

 const sc = (config.screen_configs && config.screen_configs[page]) || {};
 const currentLayout = sc.layout || config.layout || 'grid';
 const showHero = sc.show_hero !== false;
 const showSearch = sc.show_search !== false;
 const showBadges = sc.show_badges !== false;

 return <View nativeID={'jinie-page-'+page} style={[s.root,{backgroundColor:bg}]}>
  <View style={s.container}>
   <View style={s.header}>
    <View style={{flex:1,marginRight:8}}>
     <Text style={[s.eyebrow,{color:config.primary}]}>CURATED FOR YOU</Text>
     <Text style={[s.brand,{color:fg,fontFamily:config.font==='serif'?Platform.select({ios:'Georgia',default:'serif'}):undefined}]}>{config.name}</Text>
    </View>
    {config.pages.includes('cart')&&<Pressable accessibilityRole="button" onPress={()=>go('cart')} style={[s.bagPill,{backgroundColor:config.secondary||'#ede5f7'}]}><Text style={{color:'#1a1824',fontWeight:'700',fontSize:11}}>🛍️ Bag · {count}</Text></Pressable>}
   </View>

   <View style={{flex:1,flexDirection:config.navigation==='sidebar'?'row':'column'}}>
   {config.navigation!=='bottom'&&navigation}
   <ScrollView contentContainerStyle={s.content}>
    {message!==''&&<Text accessibilityRole="alert" style={[s.notice,{color:fg}]}>{message}</Text>}

    {/* HOME SCREEN */}
    {page==='home'&&<>
     {showHero&&<View style={[s.hero,{backgroundColor:config.primary}]}>
      <Text style={s.heroSmall}>A LITTLE EVERYDAY EXTRAORDINARY</Text>
      <Text style={s.heroTitle}>{sc.title || "Good things.\nGreat discoveries."}</Text>
      <Text style={s.heroBody}>{sc.subtitle || ("Explore our carefully chosen " + config.business + " collection.")}</Text>
      {config.pages.includes('products')&&<Pressable accessibilityRole="button" onPress={()=>go('products')} style={s.heroBtn}><Text style={{color:config.primary,fontWeight:'700',fontSize:11}}>Explore collection →</Text></Pressable>}
     </View>}
     {showSearch&&input('Search ' + config.business + ' products…',query,setQuery)}
     <View style={s.row}>{['All',...new Set(config.products.map(p=>p.category))].map(c=><Pressable accessibilityRole="button" key={c} onPress={()=>setCategory(c)} style={[s.chip,{backgroundColor:category===c?config.primary:dark?'#302a40':'#eeeaf5'}]}><Text style={{color:category===c?'white':dark?'#f6f3ff':'#453d52',fontWeight:'700',fontSize:10}}>{c}</Text></Pressable>)}</View>
     <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginTop:4,marginBottom:6}}>
      <Text style={[s.heading,{color:fg}]}>{sc.title ? sc.title.split('\n')[0] : 'The Latest Selection'}</Text>
      <Text style={{fontSize:10,color:config.primary,fontWeight:'700'}}>See all ({filtered.length})</Text>
     </View>
     <View style={[s.grid,currentLayout==='editorial'&&{flexDirection:'column'}]}>
      {filtered.map(p=><View key={p.id} style={{width:currentLayout==='editorial'?'100%':currentLayout==='cards'?'100%':'48%',minWidth:130,flexGrow:1}}>
       <ProductCard horizontal={currentLayout==='cards'} showBadge={showBadges} product={p} primary={config.primary} dark={dark} onOpen={()=>{setSelected(p);if(config.pages.includes('detail'))go('detail');}} onAdd={config.pages.includes('cart')?()=>add(p):null}/>
      </View>)}
     </View>
     {filtered.length===0&&<Text style={{color:muted,fontSize:11,marginVertical:12}}>No products match your search.</Text>}
    </>}

    {/* PRODUCTS SCREEN */}
    {page==='products'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "All Products & Menu"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:8}]}>{sc.subtitle || ("Browse our complete " + config.business + " catalogue")}</Text>
     {showSearch&&input('Filter ' + config.business + ' items…',query,setQuery)}
     <View style={s.row}>{['All',...new Set(config.products.map(p=>p.category))].map(c=><Pressable accessibilityRole="button" key={c} onPress={()=>setCategory(c)} style={[s.chip,{backgroundColor:category===c?config.primary:dark?'#302a40':'#eeeaf5'}]}><Text style={{color:category===c?'white':dark?'#f6f3ff':'#453d52',fontWeight:'700',fontSize:10}}>{c}</Text></Pressable>)}</View>
     <View style={[s.grid,currentLayout==='editorial'&&{flexDirection:'column'}]}>
      {filtered.map(p=><View key={p.id} style={{width:currentLayout==='editorial'?'100%':currentLayout==='cards'?'100%':'48%',minWidth:130,flexGrow:1}}>
       <ProductCard horizontal={currentLayout==='cards'} showBadge={showBadges} product={p} primary={config.primary} dark={dark} onOpen={()=>{setSelected(p);if(config.pages.includes('detail'))go('detail');}} onAdd={config.pages.includes('cart')?()=>add(p):null}/>
      </View>)}
     </View>
     {filtered.length===0&&<Text style={{color:muted,fontSize:11,marginVertical:12}}>No products match your search.</Text>}
    </>}

    {/* SEARCH SCREEN */}
    {page==='search'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "Search & Discover"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:8}]}>{sc.subtitle || ("Find your favourite " + config.business + " items")}</Text>
     {input('Search by name or category…',query,setQuery)}
     <Text style={[s.body,{fontWeight:'700',color:muted,marginTop:4}]}>Popular Searches</Text>
     <View style={s.row}>{['Top Rated', 'Deals', 'Essentials', 'Combos'].map(tag=><Pressable accessibilityRole="button" key={tag} onPress={()=>setQuery(tag==='Top Rated'?'':tag)} style={[s.chip,{backgroundColor:dark?'#302a40':'#eeeaf5'}]}><Text style={{color:dark?'#f6f3ff':'#463c55',fontWeight:'600',fontSize:10}}>{tag}</Text></Pressable>)}</View>
     <View style={[s.grid,currentLayout==='editorial'&&{flexDirection:'column'}]}>
      {filtered.map(p=><View key={p.id} style={{width:currentLayout==='editorial'?'100%':currentLayout==='cards'?'100%':'48%',minWidth:130,flexGrow:1}}>
       <ProductCard horizontal={currentLayout==='cards'} showBadge={showBadges} product={p} primary={config.primary} dark={dark} onOpen={()=>{setSelected(p);if(config.pages.includes('detail'))go('detail');}} onAdd={config.pages.includes('cart')?()=>add(p):null}/>
      </View>)}
     </View>
     {filtered.length===0&&<Text style={{color:muted,fontSize:11,marginVertical:12}}>No products match your search.</Text>}
    </>}

    {/* DETAIL SCREEN */}
    {page==='detail'&&selected&&<>
     <View style={[s.art,{backgroundColor:dark?'#2c253b':'#f4effa',overflow:'hidden',position:'relative'}]}>
      {selected.image_url ? (
       <Image source={{uri:selected.image_url}} style={{width:'100%',height:'100%'}} resizeMode="cover"/>
      ) : (
       <Text style={{fontSize:70}}>{selected.icon || '✦'}</Text>
      )}
      {Boolean(showBadges && selected.badge)&&<View style={[s.detailBadge,{backgroundColor:config.primary}]}><Text style={{color:'white',fontWeight:'800',fontSize:9}}>{selected.badge}</Text></View>}
     </View>
     <View style={s.detailMeta}>
      <Text style={[s.eyebrow,{color:config.primary}]}>{selected.category || 'Featured Collection'}</Text>
      {Boolean(selected.rating)&&<Text style={s.detailRating}>★ {selected.rating} Customer Rating</Text>}
     </View>
     <Text style={[s.heading,{color:fg,fontSize:18}]}>{selected.name}</Text>
     <Text style={[s.price,{color:config.accent||'#b98849'}]}>Rs. {selected.price.toLocaleString()}</Text>
     <Text style={[s.body,{color:muted,lineHeight:16}]}>{selected.description}</Text>
     {config.pages.includes('cart')&&button('Add to bag · Rs. ' + selected.price.toLocaleString(),()=>add(selected))}
     {button('← Back to collection',()=>go(config.pages.includes('products')?'products':'home'),true)}
    </>}

    {/* CART SCREEN */}
    {page==='cart'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "Your Shopping Bag"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:10}]}>{sc.subtitle || (count > 0 ? (count + " item" + (count===1?"":"s") + " selected") : "Your bag is empty. Discover something you love.")}</Text>
     {config.products.filter(p=>cart[p.id]).map(p=><View key={p.id} style={s.cartRow}>
      <View style={{width:52,height:52,borderRadius:12,backgroundColor:dark?'#302a40':'#eeeaf6',alignItems:'center',justifyContent:'center',overflow:'hidden'}}>
       {p.image_url ? (
        <Image source={{uri:p.image_url}} style={{width:'100%',height:'100%'}} resizeMode="cover"/>
       ) : (
        <Text style={{fontSize:24}}>{p.icon || '✦'}</Text>
       )}
      </View>
      <View style={{flex:1}}>
       <Text style={{color:fg,fontWeight:'700',fontSize:12}}>{p.name}</Text>
       <Text style={{color:muted,fontSize:11}}>Rs. {(p.price*cart[p.id]).toLocaleString()}</Text>
      </View>
      <View style={s.row}>
       <Pressable accessibilityRole="button" accessibilityLabel={'Decrease '+p.name} onPress={()=>quantity(p.id,-1)} style={[s.qtyBtn,{backgroundColor:dark?'#302a40':'#eeeaf6'}]}><Text style={{color:fg,fontSize:14,fontWeight:'700'}}>−</Text></Pressable>
       <Text accessibilityLabel={'Quantity '+p.name} style={{color:fg,fontWeight:'800',marginHorizontal:6,fontSize:12}}>{cart[p.id]}</Text>
       <Pressable accessibilityRole="button" accessibilityLabel={'Increase '+p.name} onPress={()=>quantity(p.id,1)} style={[s.qtyBtn,{backgroundColor:dark?'#302a40':'#eeeaf6'}]}><Text style={{color:config.primary,fontSize:14,fontWeight:'700'}}>+</Text></Pressable>
      </View>
     </View>)}
     <View style={[s.orderSummary,{backgroundColor:dark?'#211c2d':'#f4f1fa'}]}>
      <View style={{flexDirection:'row',justifyContent:'space-between',marginBottom:4}}><Text style={{color:muted,fontSize:11}}>Subtotal</Text><Text style={{color:fg,fontWeight:'700',fontSize:11}}>Rs. {total.toLocaleString()}</Text></View>
      <View style={{flexDirection:'row',justifyContent:'space-between',marginBottom:4}}><Text style={{color:muted,fontSize:11}}>Standard Delivery</Text><Text style={{color:'#15803d',fontWeight:'700',fontSize:11}}>FREE</Text></View>
      <View style={{borderTopWidth:1,borderColor:dark?'#342e42':'rgba(0,0,0,0.08)',paddingTop:6,flexDirection:'row',justifyContent:'space-between'}}><Text style={[s.heading,{color:fg,marginVertical:0,fontSize:14}]}>Total</Text><Text style={[s.price,{color:config.accent||'#b98849',marginVertical:0,fontSize:14}]}>Rs. {total.toLocaleString()}</Text></View>
     </View>
     {count>0&&config.pages.includes('checkout')&&button('Proceed to Checkout →',()=>go('checkout'))}
    </>}

    {/* CHECKOUT SCREEN */}
    {page==='checkout'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "Checkout & Delivery"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:10}]}>{sc.subtitle || "Cash on Delivery (COD) · Local order demo"}</Text>
     {order&&<View style={s.notice}><Text style={{color:fg,fontWeight:'700',fontSize:11}}>Order {order.id} saved · Rs. {order.total.toLocaleString()} — Ready for delivery!</Text></View>}
     <Text style={{fontSize:10,fontWeight:'700',color:muted,marginBottom:2}}>Full Name</Text>
     {input('Full name',customer,setCustomer)}
     <Text style={{fontSize:10,fontWeight:'700',color:muted,marginBottom:2,marginTop:6}}>Delivery Address</Text>
     {input('Delivery address',address,setAddress)}
     <View style={[s.paymentCard,{backgroundColor:dark?'#251f33':'rgba(124, 92, 224, 0.08)',borderColor:config.primary+'40'}]}>
      <Text style={{fontSize:18}}>💵</Text>
      <View style={{flex:1}}>
       <Text style={{color:fg,fontWeight:'800',fontSize:11}}>Cash on Delivery</Text>
       <Text style={{color:muted,fontSize:9}}>Pay upon doorstep arrival. Zero online risk.</Text>
      </View>
     </View>
     <Text style={[s.heading,{color:fg,fontSize:14,marginTop:6}]}>Total · Rs. {total.toLocaleString()}</Text>
     {button('Place Demo Order · Rs. ' + total.toLocaleString(),place)}
     <Text style={[s.body,{color:muted,fontSize:10,textAlign:'center'}]}>{orders.length} saved demo order(s) on this device</Text>
    </>}

    {/* CONTACT SCREEN */}
    {page==='contact'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "Let's Talk"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:12}]}>{sc.subtitle || ("We would love to help you find the right fit for your " + config.business + " needs.")}</Text>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <Text style={[s.eyebrow,{color:config.primary}]}>EMAIL US</Text>
      <Text style={{color:fg,fontWeight:'700',fontSize:12}}>concierge@{config.name.toLowerCase().replace(/\s+/g,'') || 'jinie'}.com</Text>
     </View>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <Text style={[s.eyebrow,{color:config.primary}]}>OPERATING HOURS</Text>
      <Text style={{color:fg,fontWeight:'700',fontSize:12}}>Mon – Sat · 9:00 AM – 9:00 PM</Text>
     </View>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <Text style={[s.eyebrow,{color:config.primary}]}>CUSTOMER CARE</Text>
      <Text style={{color:muted,fontSize:11}}>Dedicated personal consultation, bespoke requests and support.</Text>
     </View>
    </>}

    {/* ABOUT SCREEN */}
    {page==='about'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "A Thoughtful Story"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:12,lineHeight:16}]}>{sc.subtitle || (config.name + " brings together carefully selected " + config.business + " essentials. Built with care, made for everyday life.")}</Text>
     <View style={[s.promiseCard,{backgroundColor:dark?'#251f33':'rgba(124, 92, 224, 0.08)',borderColor:config.primary+'30'}]}>
      <Text style={{color:fg,fontWeight:'800',fontSize:13,marginBottom:4}}>Our Quality Promise</Text>
      <Text style={{color:muted,fontSize:11,lineHeight:16}}>Authentic sourcing, community integrity, and long-lasting durability across every item in our {config.business} collection.</Text>
     </View>
    </>}

    {/* SETTINGS SCREEN */}
    {page==='settings'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "App Settings & Preferences"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:12}]}>{sc.subtitle || "Customize your application experience and regional options."}</Text>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}>
       <View><Text style={{color:fg,fontWeight:'700',fontSize:12}}>Push Notifications</Text><Text style={{color:muted,fontSize:10}}>Order status alerts and promotional discounts</Text></View>
       <Pressable accessibilityRole="button" onPress={()=>setNotifications(!notifications)} style={[s.toggleBtn,{backgroundColor:notifications?config.primary:(dark?'#302a40':'#eeeaf5')}]}><Text style={{color:notifications?'white':muted,fontSize:10,fontWeight:'700'}}>{notifications?'ON':'OFF'}</Text></Pressable>
      </View>
     </View>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}>
       <View><Text style={{color:fg,fontWeight:'700',fontSize:12}}>Currency & Region</Text><Text style={{color:muted,fontSize:10}}>Pakistani Rupee (PKR · Rs.)</Text></View>
       <Text style={{color:config.primary,fontWeight:'800',fontSize:11}}>PKR 🇵🇰</Text>
      </View>
     </View>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}>
       <View><Text style={{color:fg,fontWeight:'700',fontSize:12}}>Language</Text><Text style={{color:muted,fontSize:10}}>Primary display language</Text></View>
       <Text style={{color:fg,fontWeight:'700',fontSize:11}}>English (Urdu ready)</Text>
      </View>
     </View>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}>
       <View><Text style={{color:fg,fontWeight:'700',fontSize:12}}>Data & Privacy</Text><Text style={{color:muted,fontSize:10}}>Local storage on this device</Text></View>
       <Pressable accessibilityRole="button" onPress={clearDemoData} style={[s.clearBtn,{backgroundColor:dark?'#3a2626':'#fee2e2'}]}><Text style={{color:'#dc2626',fontWeight:'700',fontSize:10}}>Clear Data</Text></Pressable>
      </View>
     </View>
    </>}

    {/* PROFILE SCREEN */}
    {page==='profile'&&<>
     <Text style={[s.heading,{color:fg}]}>{sc.title || "My Profile"}</Text>
     <Text style={[s.body,{color:muted,marginTop:-4,marginBottom:12}]}>{sc.subtitle || "Account overview and order history"}</Text>
     <View style={[s.profileCard,{backgroundColor:cardBg}]}>
      <View style={[s.avatarCircle,{backgroundColor:config.primary}]}><Text style={{color:'white',fontWeight:'800',fontSize:16}}>AK</Text></View>
      <View style={{flex:1}}>
       <Text style={{color:fg,fontWeight:'800',fontSize:14}}>Ahmed Khan</Text>
       <Text style={{color:muted,fontSize:10}}>ahmed.khan@example.com</Text>
       <View style={[s.tierBadge,{backgroundColor:config.primary+'20'}]}><Text style={{color:config.primary,fontWeight:'700',fontSize:9}}>★ Gold Member · {orders.length} Order{orders.length===1?'':'s'}</Text></View>
      </View>
     </View>
     <View style={s.statsStrip}>
      <View style={[s.statBox,{backgroundColor:cardBg}]}><Text style={[s.statNum,{color:config.primary}]}>{orders.length}</Text><Text style={{color:muted,fontSize:9}}>Orders</Text></View>
      <View style={[s.statBox,{backgroundColor:cardBg}]}><Text style={[s.statNum,{color:config.primary}]}>5</Text><Text style={{color:muted,fontSize:9}}>Wishlist</Text></View>
      <View style={[s.statBox,{backgroundColor:cardBg}]}><Text style={[s.statNum,{color:config.primary}]}>450</Text><Text style={{color:muted,fontSize:9}}>Points</Text></View>
     </View>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <Text style={[s.eyebrow,{color:config.primary}]}>DEFAULT SHIPPING ADDRESS</Text>
      <Text style={{color:fg,fontWeight:'700',fontSize:11,marginTop:2}}>{address}</Text>
     </View>
     <View style={[s.infoBox,{backgroundColor:cardBg}]}>
      <Text style={[s.eyebrow,{color:config.primary}]}>PAYMENT METHOD</Text>
      <Text style={{color:fg,fontWeight:'700',fontSize:11,marginTop:2}}>Cash on Delivery (Default)</Text>
     </View>
    </>}

    {/* FALLBACK FOR ANY OTHER CUSTOM PAGE */}
    {!['home','products','detail','cart','checkout','contact','about','search','settings','profile'].includes(page)&&<View style={{paddingVertical:12}}>
     <Text style={[s.heading,{color:fg}]}>{sc.title || (page.charAt(0).toUpperCase() + page.slice(1))}</Text>
     <Text style={[s.body,{color:muted}]}>{sc.subtitle || ("Explore the " + page + " screen.")}</Text>
     <View style={s.notice}><Text style={{color:fg,fontSize:11}}>Custom {page} screen crafted for {config.name}.</Text></View>
    </View>}

    <Text style={[s.footer,{color:muted}]}>Made with Jinie · Responsive React Native & Web Experience</Text>
   </ScrollView>
   {config.navigation==='bottom'&&navigation}
   </View>
  </View>
 </View>;
}

const s=StyleSheet.create({
 root:{flex:1,alignItems:'center',width:'100%'},
 container:{width:'100%',maxWidth:480,flex:1},
 header:{paddingHorizontal:16,paddingVertical:10,flexDirection:'row',justifyContent:'space-between',alignItems:'center',borderBottomWidth:1,borderColor:'rgba(0,0,0,0.04)'},
 eyebrow:{fontSize:8,letterSpacing:1.5,fontWeight:'800',textTransform:'uppercase'},
 brand:{fontSize:18,fontWeight:'800',letterSpacing:-0.5,marginTop:2},
 bagPill:{borderRadius:20,paddingVertical:5,paddingHorizontal:12},
 content:{paddingHorizontal:16,paddingTop:12,paddingBottom:24,gap:8},
 hero:{borderRadius:18,padding:16,marginBottom:10,shadowColor:'#000',shadowOpacity:0.08,shadowRadius:10,elevation:3},
 heroSmall:{color:'rgba(255,255,255,0.85)',fontSize:8,letterSpacing:1.5,fontWeight:'800'},
 heroTitle:{fontSize:18,lineHeight:22,color:'white',fontWeight:'800',marginVertical:6},
 heroBody:{color:'rgba(255,255,255,0.9)',lineHeight:15,marginBottom:10,fontSize:11},
 heroBtn:{backgroundColor:'rgba(255,255,255,0.95)',borderRadius:10,paddingVertical:6,paddingHorizontal:12,alignSelf:'flex-start'},
 heading:{fontFamily:config.font==='serif'?Platform.select({ios:'Georgia',default:'serif'}):undefined,fontSize:15,fontWeight:'800',marginVertical:4},
 body:{fontSize:11,lineHeight:16,marginVertical:2},
 button:{paddingVertical:8,paddingHorizontal:14,borderRadius:12,alignItems:'center',justifyContent:'center',marginVertical:4},
 row:{flexDirection:'row',gap:6,alignItems:'center',marginVertical:4,flexWrap:'wrap'},
 chip:{paddingVertical:5,paddingHorizontal:12,borderRadius:20},
 grid:{flexDirection:'row',flexWrap:'wrap',gap:10,justifyContent:'space-between'},
 input:{borderWidth:1,paddingVertical:7,paddingHorizontal:10,borderRadius:10,marginVertical:3,fontSize:11},
 price:{fontSize:14,fontWeight:'800',marginVertical:3},
 art:{height:180,borderRadius:18,alignItems:'center',justifyContent:'center',marginBottom:6},
 detailBadge:{position:'absolute',top:10,left:10,paddingHorizontal:8,paddingVertical:3,borderRadius:8},
 detailMeta:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginTop:6},
 detailRating:{fontSize:10,fontWeight:'700',color:'#eab308'},
 cartRow:{flexDirection:'row',gap:10,alignItems:'center',paddingVertical:8,borderBottomWidth:1,borderColor:'rgba(0,0,0,0.06)'},
 qtyBtn:{width:22,height:22,borderRadius:6,alignItems:'center',justifyContent:'center'},
 orderSummary:{padding:12,borderRadius:14,marginVertical:8,gap:4},
 paymentCard:{padding:10,borderRadius:12,flexDirection:'row',gap:8,alignItems:'center',marginVertical:6,borderWidth:1},
 infoBox:{padding:10,borderRadius:12,marginVertical:3,gap:3,borderWidth:1,borderColor:'rgba(0,0,0,0.06)'},
 promiseCard:{padding:12,borderRadius:14,borderWidth:1,marginVertical:6},
 toggleBtn:{paddingVertical:4,paddingHorizontal:10,borderRadius:12},
 clearBtn:{paddingVertical:4,paddingHorizontal:8,borderRadius:8},
 profileCard:{padding:12,borderRadius:14,flexDirection:'row',gap:12,alignItems:'center',marginBottom:8,borderWidth:1,borderColor:'rgba(0,0,0,0.06)'},
 avatarCircle:{width:44,height:44,borderRadius:22,alignItems:'center',justifyContent:'center'},
 tierBadge:{paddingHorizontal:8,paddingVertical:2,borderRadius:8,alignSelf:'flex-start',marginTop:4},
 statsStrip:{flexDirection:'row',gap:8,marginBottom:8},
 statBox:{flex:1,padding:10,borderRadius:12,alignItems:'center',borderWidth:1,borderColor:'rgba(0,0,0,0.06)'},
 statNum:{fontSize:16,fontWeight:'800',marginBottom:2},
 nav:{maxHeight:52,minHeight:52,borderTopWidth:1,borderColor:'rgba(0,0,0,0.06)'},
 tab:{paddingVertical:3,paddingHorizontal:6,borderRadius:8,alignItems:'center',justifyContent:'center'},
 notice:{padding:8,backgroundColor:'#aa92e325',borderRadius:10,marginBottom:6},
 footer:{fontSize:10,textAlign:'center',marginTop:20,marginBottom:10}
});
