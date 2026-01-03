import { Settings as SettingsIcon, Sliders, Server, Users, Shield, Lock, Save, Bell } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function Settings() {
  return (
    <MainLayout title="Settings" description="System configuration and preferences">
      <div className="grid grid-cols-1 gap-4 md:gap-6 lg:grid-cols-2">
        {/* Decision Engine Settings */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sliders className="h-5 w-5 text-primary" />
              Decision Engine
            </CardTitle>
            <CardDescription>Configure routing decision parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Minimum Confidence Threshold</Label>
              <div className="flex items-center gap-4">
                <Slider defaultValue={[75]} max={100} step={5} className="flex-1" />
                <span className="font-mono text-sm w-12">75%</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Decisions below this threshold will require manual review
              </p>
            </div>

            <div className="space-y-2">
              <Label>Default Optimization Strategy</Label>
              <Select defaultValue="balanced">
                <SelectTrigger className="bg-secondary/30">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cost">Cost-Optimized</SelectItem>
                  <SelectItem value="performance">Performance-Optimized</SelectItem>
                  <SelectItem value="balanced">Balanced</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Auto-Execute High Confidence</Label>
                <p className="text-xs text-muted-foreground">
                  Automatically execute decisions above 90% confidence
                </p>
              </div>
              <Switch />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Enable Hybrid Fallback</Label>
                <p className="text-xs text-muted-foreground">
                  Fall back to hybrid execution if quantum fails
                </p>
              </div>
              <Switch defaultChecked />
            </div>
          </CardContent>
        </Card>

        {/* Hardware Preferences */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5 text-primary" />
              Hardware Preferences
            </CardTitle>
            <CardDescription>Set default hardware and provider preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Preferred Quantum Provider</Label>
              <Select defaultValue="auto">
                <SelectTrigger className="bg-secondary/30">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto (Best Available)</SelectItem>
                  <SelectItem value="ibm">IBM Quantum</SelectItem>
                  <SelectItem value="braket">Amazon Braket</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Max Queue Wait Time</Label>
              <div className="flex items-center gap-4">
                <Input type="number" defaultValue={10} className="bg-secondary/30 w-24" />
                <span className="text-sm text-muted-foreground">minutes</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Reserve Capacity</Label>
                <p className="text-xs text-muted-foreground">
                  Reserve dedicated hardware slots
                </p>
              </div>
              <Switch />
            </div>

            <div className="space-y-2">
              <Label>Minimum Qubit Requirement</Label>
              <Select defaultValue="20">
                <SelectTrigger className="bg-secondary/30">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10+ Qubits</SelectItem>
                  <SelectItem value="20">20+ Qubits</SelectItem>
                  <SelectItem value="50">50+ Qubits</SelectItem>
                  <SelectItem value="100">100+ Qubits</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-primary" />
              Notifications
            </CardTitle>
            <CardDescription>Configure alert and notification preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Execution Completed</Label>
                <p className="text-xs text-muted-foreground">Notify when jobs finish</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Execution Failed</Label>
                <p className="text-xs text-muted-foreground">Alert on job failures</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Budget Alerts</Label>
                <p className="text-xs text-muted-foreground">Spending threshold warnings</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>System Maintenance</Label>
                <p className="text-xs text-muted-foreground">Scheduled downtime notices</p>
              </div>
              <Switch defaultChecked />
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Security
            </CardTitle>
            <CardDescription>Manage access and authentication settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>API Key</Label>
              <div className="flex gap-2">
                <Input type="password" value="••••••••••••••••" readOnly className="bg-secondary/30" />
                <Button variant="outline">Regenerate</Button>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Two-Factor Authentication</Label>
                <p className="text-xs text-muted-foreground">Add extra security layer</p>
              </div>
              <Switch />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Session Timeout</Label>
                <p className="text-xs text-muted-foreground">Auto-logout after inactivity</p>
              </div>
              <Select defaultValue="30">
                <SelectTrigger className="w-32 bg-secondary/30">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="15">15 minutes</SelectItem>
                  <SelectItem value="30">30 minutes</SelectItem>
                  <SelectItem value="60">1 hour</SelectItem>
                  <SelectItem value="never">Never</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="lg:col-span-2 flex justify-end gap-3">
          <Button variant="outline">Cancel</Button>
          <Button variant="quantum" className="gap-2">
            <Save className="h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </div>
    </MainLayout>
  );
}
