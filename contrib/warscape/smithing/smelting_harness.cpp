
#include "WarscapeSkillsAddon.h"
#include "WarscapeSmelting.h"
#include <vector>
#include <iostream>
#include <stdexcept>
#include <cstdarg>
#include <charconv>
#include <sstream>
#include <string_view>
using uint8=std::uint8_t; using uint32=std::uint32_t;
int checks=0;
#define CHECK(...) do { ++checks; if(!(__VA_ARGS__)) { std::cerr << "failed check " << checks << ": " << #__VA_ARGS__ << '\\n'; throw std::runtime_error(#__VA_ARGS__); } } while(0)
#define ASSERT CHECK
constexpr uint8 INVENTORY_SLOT_BAG_0=255, INVENTORY_SLOT_ITEM_START=0, INVENTORY_SLOT_ITEM_END=4;
constexpr uint8 INVENTORY_SLOT_BAG_START=4, INVENTORY_SLOT_BAG_END=4, NULL_BAG=254, NULL_SLOT=254;
constexpr int EQUIP_ERR_OK=0, EMOTE_STATE_WORK_MINING=1, GAMEOBJECT_TYPE_SPELL_FOCUS=8;
struct Position { float x=0,y=0,z=0; void Relocate(Position const* p){x=p->x;y=p->y;z=p->z;} float GetExactDist(Position const* p) const{return std::sqrt((x-p->x)*(x-p->x)+(y-p->y)*(y-p->y)+(z-p->z)*(z-p->z));} };
struct WorldObject:Position {};
struct Info { int type=8; struct {uint32 focusId=3;float dist=10;} spellFocus; };
struct ObjectGuid { uint32 id=1; bool IsEmpty()const{return !id;} void Clear(){id=0;} };
struct GameObject:WorldObject { uint32 GetEntry(){return 173063;} int GetGoType(){return info.type;} ObjectGuid GetGUID(){return {};} Info info; bool spawned=true;float orientation=0; Info* GetGOInfo(){return &info;} bool isSpawned(){return spawned;} bool IsWithinDistInMap(WorldObject const* p,float d){return GetExactDist(p)<=d;} bool IsAtInteractDistance(Position const& p,float d){d=std::min(d,4.0f);float const cx=-0.2775344f,cy=2.238683f;float wx=x+cx*std::cos(orientation)-cy*std::sin(orientation),wy=y+cx*std::sin(orientation)+cy*std::cos(orientation);float dx=p.x-wx,dy=p.y-wy,dz=p.z-z;return dx*dx+dy*dy+dz*dz<=d*d;} };
namespace Trinity {
// NATIVE FOCUS PREDICATE
}
std::vector<GameObject*> focuses;
namespace Trinity { template<class Check> struct GameObjectSearcher {GameObject*& result;Check& check; GameObjectSearcher(WorldObject const*,GameObject*& r,Check& c):result(r),check(c){} }; }
namespace Cell { template<class C> void VisitGridObjects(WorldObject const*,Trinity::GameObjectSearcher<C>& s,float){for(auto* g:focuses)if(s.check(g))s.result=g;} }
struct ItemTemplate {uint32 GetMaxStackSize() const{return 1;}};
struct ObjectMgr {ItemTemplate item;ItemTemplate const* GetItemTemplate(uint32) const{return &item;}} mgr;
auto* sObjectMgr=&mgr;
struct Config {int duration=3000;int GetIntDefault(char const*,int,bool){return duration;}} config;
auto* sConfigMgr=&config;
struct Session {bool logout=false,disconnected=false; bool isLogingOut(){return logout;}bool PlayerDisconnected(){return disconnected;}void SendNotification(char const*,...){} };
struct Dest {uint32 pos,count;}; using ItemPosCountVec=std::vector<Dest>;
struct Player;
struct Item {uint32 entry,count,pos;bool trade=false; static bool fail; uint32 GetEntry(){return entry;}uint32 GetCount(){return count;}bool IsInTrade(){return trade;}uint32 GetGUID(){return pos+1;}uint8 GetBagSlot(){return 255;}uint8 GetSlot(){return uint8(pos);}static Item* CreateItem(uint32 e,uint32 c,Player*){return fail?nullptr:new Item{e,c,0};}};
bool Item::fail=false;
struct Bag {uint32 GetBagSize(){return 0;}};
constexpr int EMOTE_STATE_NONE=0, EMOTE_STATE_USE_STANDING=2,CHAT_MSG_WHISPER=0,LANG_ADDON=0,LOCALE_enUS=0;
namespace WorldPackets { namespace Chat { struct Chat {std::string text; template<class... T> void Initialize(int,int,Player*,Player*,std::string const& m,T...){text=m;} std::string* Write(){return &text;}};}}
namespace ObjectAccessor { GameObject* GetGameObject(Player const&, ObjectGuid); }
struct Player:WorldObject {
 enum class RS_Skill {Mining,Smithing};
 Session session;bool alive=true,combat=false,moving=false,teleport=false,trade=false,casting=false,world=true;int emote=0;
 ObjectGuid warscapeForge;uint32 warscapeForgeSerial=1,warscapeForgeSequence=0,warscapeBatch=0,warscapeForgeRefresh=0;bool warscapeSmeltingMenuOpen=true;
 bool phase=true;std::vector<std::string> messages;
 uint32 warscapeSmeltRemaining=0,warscapeSmeltMap=0,warscapeSmeltRequestCooldown=0;Position warscapeSmeltStart;
 uint8 warscapeSmithingTenthXP=0,warscapeMiningHalfXP=0;bool _warscapeSkillsDirty=false;
 Warscape::SkillProgress smithing;Item* slots[4]={};int saves=0,bars=0;uint32 savedXP=0;uint8 savedCarry=0;
 ~Player(){for(auto* i:slots)delete i;}
 void ore(uint32 slot,uint32 id,uint32 count){delete slots[slot];slots[slot]=new Item{id,count,slot};}
 bool IsWarscapeSmelting()const{return warscapeSmeltRemaining!=0;}
 void SetEmoteState(int n){emote=n;}
 bool HasWarscapeForge()const; void OpenWarscapeSmelting(GameObject*);void CloseWarscapeSmelting();void RefreshWarscapeSmelting(uint32);void SendWarscapeSmelting(std::string const&);bool HandleWarscapeSmelting(std::string_view,std::string const&,bool);
 bool InSamePhase(GameObject*)const{return phase;}std::string GetName()const{return "Tester";}
 void SendDirectMessage(std::string* m){messages.push_back(*m);}uint32 GetItemCount(uint32 id){uint32 n=0;for(auto* i:slots)if(i&&i->entry==id)n+=i->count;return n;}
 void CancelWarscapeSmelting();void StartWarscapeBronzeSmelting();void UpdateWarscapeSmelting(uint32);
 bool HasWarscapeCraftingFocus(uint32)const;bool PrepareWarscapeBronze(Item*&,Item*&,ItemPosCountVec&)const;
 void AddRSSkillTenthXP(RS_Skill,uint32);void AddRSSkillHalfXP(RS_Skill,uint32);
 void AddRSSkillXP(RS_Skill skill,uint32 n){if(skill==RS_Skill::Smithing)Warscape::AddSkillXP(smithing,n);}
 Session* GetSession(){return &session;}bool IsInWorld(){return world;}bool IsAlive(){return alive;}bool IsInCombat(){return combat;}bool isMoving(){return moving;}bool IsBeingTeleported(){return teleport;}bool GetTradeData(){return trade;}bool IsNonMeleeSpellCast(bool){return casting;}int GetEmoteState(){return emote;}
 uint32 GetMapId(){return 0;}float GetVisibilityRange()const{return 100;}uint8 GetRSSkillLevel(RS_Skill){return smithing.Level;}
 Item* GetItemByPos(uint8,uint8 slot)const{return slot<4?slots[slot]:nullptr;}Item* GetItemByPos(uint32 pos)const{return GetItemByPos(255,uint8(pos));}Bag* GetBagByPos(uint8)const{return nullptr;}uint32 GetLootGUID()const{return 0;}
 int CanStoreNewItem(uint8,uint8,ItemPosCountVec& d,uint32,uint32)const{for(uint32 i=0;i<4;++i)if(!slots[i]){d.push_back({i,1});return 0;}return 1;}
 int CanStoreItem(uint8,uint8 slot,ItemPosCountVec& d,uint32,uint32,Item*,bool swap)const{CHECK(swap);d.push_back({slot,1});return 0;}
 void DestroyItemCount(Item* item,uint32& c,bool){CHECK(c==1);if(--item->count==0){slots[item->pos]=nullptr;delete item;}c=0;}
 Item* StoreItem(ItemPosCountVec const& d,Item* bar,bool){CHECK(d.size()==1);CHECK(!slots[d[0].pos]);bar->pos=d[0].pos;slots[bar->pos]=bar;++bars;return bar;}
 void ItemAddedQuestCheck(uint32,uint32){}void SendNewItem(Item*,uint32,bool,bool){}
 void SaveToDB(){++saves;savedXP=smithing.XP;savedCarry=warscapeSmithingTenthXP;}
};
namespace ObjectAccessor {GameObject* GetGameObject(Player const&,ObjectGuid g){return g.id&&!focuses.empty()?focuses[0]:nullptr;}}
// PRODUCTION METHODS
void fill(Player& p,uint32 count=1){p.ore(0,2770,count);p.ore(1,900201,count);}
int main(){
 CHECK(Warscape::SmeltingRecipes.size()==8);
 const char* expected[]={"bronze","iron","steel","silver","gold","mithril","adamant","rune"};
 for(size_t i=0;i<8;++i){
  const auto& r=Warscape::SmeltingRecipes[i];
  CHECK(std::string(r.Id)==expected[i]);
  CHECK(r.Implemented==(i==0));
  if(i){CHECK(r.BarItem==0&&r.SmithingLevel==0&&r.XPTenths==0&&r.DurationMs==0);CHECK(r.Ingredients[0].Count==0&&r.Ingredients[1].Count==0);}
 }
 CHECK(Warscape::SmeltingRecipes[0].Guaranteed);
 CHECK(Warscape::SmeltingRecipes[0].SmithingLevel==1&&Warscape::SmeltingRecipes[0].DurationMs==3000);

 GameObject forge;focuses={&forge};
 {Player p;fill(p);p.StartWarscapeBronzeSmelting();CHECK(p.warscapeSmeltRemaining==3000);p.StartWarscapeBronzeSmelting();p.UpdateWarscapeSmelting(2999);CHECK(!p.bars&&p.slots[0]);p.UpdateWarscapeSmelting(1);CHECK(p.bars==1&&p.smithing.XP==6&&p.warscapeSmithingTenthXP==2&&p.saves==1);p.UpdateWarscapeSmelting(9999);CHECK(p.bars==1);Player reload;Warscape::SetSkillXP(reload.smithing,p.savedXP,false);reload.warscapeSmithingTenthXP=p.savedCarry;for(int n=0;n<4;++n)reload.AddRSSkillTenthXP(Player::RS_Skill::Smithing,62);CHECK(reload.smithing.XP==31&&reload.warscapeSmithingTenthXP==0);}
 {Player p;fill(p);p.warscapeSmithingTenthXP=5;p.AddRSSkillTenthXP(Player::RS_Skill::Smithing,62);CHECK(p.smithing.XP==6&&p.warscapeSmithingTenthXP==7);p.AddRSSkillHalfXP(Player::RS_Skill::Smithing,1);CHECK(p.smithing.XP==7&&p.warscapeSmithingTenthXP==2);}
 for(int mode=0;mode<4;++mode){Player p;fill(p);forge.info.spellFocus.focusId=mode==0?1:3;forge.spawned=mode!=1;forge.x=mode==2?11.4f:0;if(mode==3)forge.info.type=5;p.StartWarscapeBronzeSmelting();CHECK(!p.IsWarscapeSmelting());CHECK(p.slots[0]&&p.bars==0);forge.info.type=8;forge.info.spellFocus.focusId=3;forge.spawned=true;forge.x=0;}
 {Player p;fill(p);forge.x=0;forge.y=0;forge.z=0;forge.orientation=0;CHECK(p.HasWarscapeForge());p.y=5.5f;CHECK(p.HasWarscapeForge());p.y=2.238683f;p.x=3.522466f;CHECK(p.HasWarscapeForge());p.x=4.3f;CHECK(!p.HasWarscapeForge());p.x=0;p.y=0;forge.orientation=1.5707963f;p.x=-2.238683f;p.y=-0.2775344f;CHECK(p.HasWarscapeForge());p.x=-2.238683f+4.01f;p.y=-0.2775344f;CHECK(!p.HasWarscapeForge());p.x=0;p.y=0;forge.orientation=0;}
 {Player p;fill(p);delete p.slots[1];p.slots[1]=nullptr;p.StartWarscapeBronzeSmelting();CHECK(!p.IsWarscapeSmelting());}
 {Player p;fill(p,2);p.ore(2,42,1);p.ore(3,42,1);p.StartWarscapeBronzeSmelting();CHECK(!p.IsWarscapeSmelting());}
 {Player p;fill(p);p.ore(2,42,1);p.ore(3,42,1);p.StartWarscapeBronzeSmelting();CHECK(p.IsWarscapeSmelting());p.UpdateWarscapeSmelting(3000);CHECK(p.bars==1&&p.smithing.XP==6);}
 {Player p;fill(p);p.slots[0]->trade=true;p.StartWarscapeBronzeSmelting();CHECK(!p.IsWarscapeSmelting());}
 {Player p;fill(p);p.StartWarscapeBronzeSmelting();Item::fail=true;p.UpdateWarscapeSmelting(3000);CHECK(p.slots[0]&&p.slots[1]&&p.bars==0&&p.smithing.XP==0);Item::fail=false;}
 {Player p;fill(p);p.StartWarscapeBronzeSmelting();delete p.slots[1];p.slots[1]=nullptr;p.UpdateWarscapeSmelting(3000);CHECK(p.slots[0]&&p.bars==0&&p.smithing.XP==0);}
 {Player p;fill(p,2);p.StartWarscapeBronzeSmelting();p.ore(2,42,1);p.ore(3,42,1);p.UpdateWarscapeSmelting(3000);CHECK(p.slots[0]->count==2&&p.bars==0);}
 for(int mode=0;mode<11;++mode){Player p;fill(p);p.StartWarscapeBronzeSmelting();CHECK(p.IsWarscapeSmelting());switch(mode){case 0:p.moving=true;break;case 1:p.combat=true;break;case 2:p.alive=false;break;case 3:p.session.logout=true;break;case 4:p.session.disconnected=true;break;case 5:p.trade=true;break;case 6:p.casting=true;break;case 7:forge.spawned=false;break;case 8:p.x=6;break;case 9:p.emote=1;break;case 10:p.CancelWarscapeSmelting();break;}p.UpdateWarscapeSmelting(3000);CHECK(!p.bars&&p.slots[0]&&p.slots[1]&&p.smithing.XP==0);forge.spawned=true;}
 {Player p;fill(p);p.smithing.Level=0;p.StartWarscapeBronzeSmelting();CHECK(!p.IsWarscapeSmelting());}

 for(uint32 q:{1u,5u,10u,0u}){Player p;fill(p,20);p.HandleWarscapeSmelting("START|1|1|bronze|"+std::to_string(q),"Tester",true);uint32 expected=q?q:3; // nonstackable bars fill four slots after two completions
  for(uint32 i=0;i<expected+2;++i)p.UpdateWarscapeSmelting(3000);
  CHECK(p.bars==int(q==1?1:2));CHECK(p.slots[0]->count==uint32(20-p.bars));CHECK(p.savedXP==uint32(p.bars*62/10));}
 {Player p;fill(p,1);p.HandleWarscapeSmelting("START|1|1|bronze|5","Tester",true);p.HandleWarscapeSmelting("START|1|1|bronze|5","Tester",true);CHECK(p.warscapeForgeSequence==1);p.UpdateWarscapeSmelting(3000);CHECK(p.bars==1);p.HandleWarscapeSmelting("START|1|1|bronze|5","Tester",true);CHECK(!p.IsWarscapeSmelting());}
 {Player p;fill(p);p.HandleWarscapeSmelting("START|1|1|bronze|1","Tester",true);CHECK(p.IsWarscapeSmelting()&&!p.warscapeSmeltingMenuOpen);CHECK(p.messages.back()=="ACCEPT|1|1");p.UpdateWarscapeSmelting(3000);CHECK(p.bars==1&&!p.IsWarscapeSmelting());}
 {Player p;fill(p);p.HandleWarscapeSmelting("START|1|1|iron|1","Tester",true);CHECK(!p.IsWarscapeSmelting());p.HandleWarscapeSmelting("START|2|1|bronze|1","Tester",true);CHECK(!p.IsWarscapeSmelting());p.HandleWarscapeSmelting("START|1|1|bronze|1","Other",true);CHECK(!p.IsWarscapeSmelting());p.HandleWarscapeSmelting("START|1|1|bronze|1","Tester",false);CHECK(!p.IsWarscapeSmelting());}
 {Player p;fill(p);p.HandleWarscapeSmelting("START|1|1|bronze|10","Tester",true);p.HandleWarscapeSmelting("CLOSE|1|2","Tester",true);CHECK(p.IsWarscapeSmelting());p.UpdateWarscapeSmelting(3000);CHECK(p.bars==1&&!p.slots[0]);}
 {Player p;fill(p);p.HandleWarscapeSmelting("START|1|1|bronze|1","Tester",true);CHECK(p.IsWarscapeSmelting()&&!p.warscapeSmeltingMenuOpen);p.x=6;p.UpdateWarscapeSmelting(3000);CHECK(!p.IsWarscapeSmelting()&&!p.bars&&p.slots[0]&&p.slots[1]&&p.smithing.XP==0);}
 {Player p;forge.x=0;forge.y=0;forge.z=0;forge.orientation=0;p.OpenWarscapeSmelting(&forge);CHECK(p.warscapeSmeltingMenuOpen);p.x=6;p.RefreshWarscapeSmelting(250);CHECK(!p.warscapeSmeltingMenuOpen&&!p.IsWarscapeSmelting());CHECK(!p.messages.empty()&&p.messages.back()=="CLOSE|2");p.x=0;}
 {Player p;fill(p);p.StartWarscapeBronzeSmelting();p.phase=false;p.UpdateWarscapeSmelting(3000);CHECK(!p.bars);}

 for(uint32 q:{5u,10u,0u}){Player p;fill(p,20);p.HandleWarscapeSmelting("START|1|1|bronze|"+std::to_string(q),"Tester",true);uint32 expected=q?q:20;
  for(uint32 n=0;n<expected;++n){p.UpdateWarscapeSmelting(3000);for(auto*& i:p.slots)if(i&&i->entry==900500){delete i;i=nullptr;}}
  CHECK(p.bars==int(expected));CHECK(!p.IsWarscapeSmelting());CHECK(p.savedXP==expected*62/10);CHECK(p.savedCarry==expected*62%10);
 }
 {Player p;fill(p);for(auto req:{"START||1|1|bronze|1","START|1|1|bronze|-1","START|1|1|bronze|2","START|1|1|bronze|1|extra"}){p.HandleWarscapeSmelting(req,"Tester",true);CHECK(!p.IsWarscapeSmelting());}}
 std::cout<<"PASS: "<<checks<<" smelting assertions (production methods, mocked engine services)\n";
}
